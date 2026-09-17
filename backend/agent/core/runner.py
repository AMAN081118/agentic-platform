"""
Agent runner — high-level interface to execute the agent.
Now with full memory integration: context loading + auto-storage.
"""

import time
from typing import Optional, AsyncGenerator
from langchain_core.messages import HumanMessage, AIMessage

from agent.core.state import AgentState
from agent.core.graph import get_agent_graph
from agent.configs.registry import get_agent_config
from db.operations import LogOps
from db.models import AgentLogCreate
from memory.short_term import ShortTermMemory
from memory.manager import MemoryManager


class AgentRunner:
    """
    Executes the agent graph for a given message.
    Handles state initialization, memory context, execution, and auto-storage.
    """

    @staticmethod
    def run(
        message: str,
        agent_type: str = "health",
        session_id: str = "",
        user_id: str = "anonymous",
        chat_history: Optional[list[dict]] = None,
    ) -> dict:
        """
        Run the agent synchronously with full memory support.

        Args:
            message: User's input message
            agent_type: Which agent config to use
            session_id: Current session ID
            user_id: Current user ID
            chat_history: Previous messages for context

        Returns:
            Dict with 'response', 'session_id', 'metadata'
        """
        config = get_agent_config(agent_type)
        graph = get_agent_graph()

        # === 1. Build Memory Context ===
        memory_context = ""
        if config.memory.long_term_enabled:
            try:
                memory_result = MemoryManager.get_context(
                    session_id=session_id,
                    user_id=user_id,
                    current_message=message,
                    memory_config=config.memory,
                )
                memory_context = memory_result.get("formatted", "")
            except Exception as e:
                print(f" Memory context error: {e}")

        # === 2. Build Message History ===
        messages = []
        if chat_history:
            for msg in chat_history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))

        # Add current message
        messages.append(HumanMessage(content=message))

        # === 3. Initialize State ===
        initial_state: AgentState = {
            "messages": messages,
            "agent_type": agent_type,
            "session_id": session_id,
            "user_id": user_id,
            "tools_output": None,
            "memory_context": memory_context if memory_context else None,
            "next_action": None,
            "tool_name": None,
            "tool_input": None,
            "final_response": None,
            "iteration": 0,
            "metadata": {},
        }

        start_time = time.time()

        # === 4. Execute Graph ===
        try:
            final_state = graph.invoke(initial_state)
            total_latency = int((time.time() - start_time) * 1000)

            response = final_state.get("final_response", "No response generated.")

            # === 5. Auto-Store Messages in Long-Term Memory ===
            try:
                # Store user message
                MemoryManager.store_message(
                    content=message,
                    session_id=session_id,
                    user_id=user_id,
                    role="user",
                    agent_type=agent_type,
                    memory_config=config.memory,
                )

                # Store assistant response
                MemoryManager.store_message(
                    content=response,
                    session_id=session_id,
                    user_id=user_id,
                    role="assistant",
                    agent_type=agent_type,
                    memory_config=config.memory,
                )
            except Exception as e:
                print(f" Auto-store memory error: {e}")

            # === 6. Log Execution ===
            try:
                LogOps.create(
                    AgentLogCreate(
                        session_id=session_id,
                        event_type="llm_call",
                        agent_type=agent_type,
                        input_data={
                            "message": message[:500],
                            "had_memory_context": bool(memory_context),
                        },
                        output_data={
                            "response": response[:500],
                            "iterations": final_state.get("iteration", 0),
                        },
                        latency_ms=total_latency,
                    )
                )
            except Exception:
                pass

            return {
                "response": response,
                "session_id": session_id,
                "iterations": final_state.get("iteration", 0),
                "latency_ms": total_latency,
                "metadata": final_state.get("metadata", {}),
                "memory_used": bool(memory_context),
            }

        except Exception as e:
            # Log error
            try:
                LogOps.create(
                    AgentLogCreate(
                        session_id=session_id,
                        event_type="error",
                        agent_type=agent_type,
                        input_data={"message": message[:500]},
                        output_data={"error": str(e)},
                        latency_ms=int((time.time() - start_time) * 1000),
                    )
                )
            except Exception:
                pass

            config = get_agent_config(agent_type)
            return {
                "response": f"{config.persona.error_message} (Error: {str(e)})",
                "session_id": session_id,
                "iterations": 0,
                "latency_ms": int((time.time() - start_time) * 1000),
                "metadata": {"error": str(e)},
                "memory_used": False,
            }

    @staticmethod
    async def run_stream(
        message: str,
        agent_type: str = "health",
        session_id: str = "",
        user_id: str = "anonymous",
        chat_history: Optional[list[dict]] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Run the agent and yield tokens for streaming.
        Runs full execution then streams result word-by-word.
        True LLM token streaming will be added in Phase 7.
        """
        result = AgentRunner.run(
            message=message,
            agent_type=agent_type,
            session_id=session_id,
            user_id=user_id,
            chat_history=chat_history,
        )

        response = result.get("response", "")

        # Stream word by word
        words = response.split()
        for word in words:
            yield word + " "