"""
Streaming handler - manages token-by-token LLM output.
Fixed: no JSON mode, pattern-based tool detection.
"""

import json
import re
import time
from typing import AsyncGenerator, Optional, Callable
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from agent.core.llm_provider import LLMProvider
from agent.configs.registry import get_agent_config
from agent.configs.base import AgentConfig


class StreamingHandler:

    @staticmethod
    async def stream_agent_response(
        message: str,
        agent_type: str = "health",
        session_id: str = "",
        user_id: str = "anonymous",
        chat_history: Optional[list[dict]] = None,
        memory_context: Optional[str] = None,
    ) -> AsyncGenerator[dict, None]:
        """
        Run the full agent loop with streaming on the final response.
        """
        config = get_agent_config(agent_type)
        iteration = 0
        max_iterations = config.max_iterations
        tools_output = None
        current_memory = memory_context

        history_messages = []
        if chat_history:
            for msg in chat_history:
                if msg["role"] == "user":
                    history_messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    history_messages.append(AIMessage(content=msg["content"]))

        history_messages.append(HumanMessage(content=message))

        yield {"type": "status", "content": "thinking"}

        while iteration < max_iterations:
            iteration += 1

            # Build system prompt
            system_parts = [config.build_system_prompt()]

            if config.tools:
                tool_names = ", ".join(config.get_tool_names())
                system_parts.append(
                    f"\n\nAVAILABLE TOOLS:\n{config.get_tool_descriptions()}\n\n"
                    "TOOL USAGE INSTRUCTIONS:\n"
                    "If you need to use a tool, write your response in this exact format:\n"
                    "TOOL_CALL: tool_name | input_value\n\n"
                    "If you want to search memory, write:\n"
                    "MEMORY_SEARCH: your search query\n\n"
                    "Otherwise just respond normally.\n"
                    f"Available tools: {tool_names}"
                )

            if current_memory:
                system_parts.append(
                    f"\n\nRELEVANT CONTEXT FROM MEMORY:\n{current_memory}\n"
                    "Use this context if relevant."
                )

            if tools_output:
                system_parts.append(
                    f"\n\nTOOL RESULT:\n{tools_output}\n"
                    "Use this result to formulate a helpful response. "
                    "Present the data clearly and add relevant context."
                )

            full_messages = [SystemMessage(content="\n".join(system_parts))]
            full_messages.extend(history_messages)

            # Decision LLM call (non-streaming)
            llm_decision = LLMProvider.get_for_decision(
                model=config.model,
                temperature=config.temperature,
            )

            try:
                response = await llm_decision.ainvoke(full_messages)
            except Exception as e:
                yield {"type": "token", "content": f"Error: {str(e)}"}
                yield {"type": "end", "content": ""}
                return

            content = response.content.strip()

            # Check for TOOL_CALL
            tool_match = re.search(
                r'TOOL_CALL:\s*(\S+)\s*\|\s*(.+?)(?:\n|$)',
                content,
                re.IGNORECASE
            )
            if tool_match:
                tool_name = tool_match.group(1).strip()
                tool_input = tool_match.group(2).strip()
                tool_config = config.get_tool_by_name(tool_name)

                yield {"type": "tool", "content": f"Using {tool_name}..."}

                if tool_config:
                    try:
                        tools_output = str(tool_config.function(tool_input))
                    except Exception as e:
                        tools_output = f"Tool error: {str(e)}"
                else:
                    tools_output = f"Tool '{tool_name}' not found."

                continue

            # Check for MEMORY_SEARCH
            memory_match = re.search(
                r'MEMORY_SEARCH:\s*(.+?)(?:\n|$)',
                content,
                re.IGNORECASE
            )
            if memory_match:
                query = memory_match.group(1).strip()
                yield {"type": "status", "content": "searching memory"}

                try:
                    from memory.manager import MemoryManager
                    results = MemoryManager.get_context(
                        session_id=session_id,
                        user_id=user_id,
                        current_message=query,
                        memory_config=config.memory,
                    )
                    current_memory = results.get("formatted", "No memories found.")
                except Exception:
                    current_memory = "Memory search failed."

                continue

            # No tool/memory needed: stream the final response
            # If we have tool output, re-generate with streaming for nicer output
            if tools_output:
                stream_messages = [
                    SystemMessage(
                        content=(
                            f"You are {config.persona.name}, {config.persona.role}. "
                            f"Tone: {config.persona.tone}.\n\n"
                            f"Tool data:\n{tools_output}\n\n"
                            "Present this data in a clear, helpful way to the user. "
                            "Add relevant context and advice. Do not mention tools or JSON."
                        )
                    ),
                    HumanMessage(content=message),
                ]

                llm_stream = LLMProvider.get(
                    model=config.model,
                    temperature=config.temperature,
                    streaming=True,
                )

                try:
                    async for chunk in llm_stream.astream(stream_messages):
                        token = chunk.content
                        if token:
                            yield {"type": "token", "content": token}
                except Exception:
                    for word in content.split():
                        yield {"type": "token", "content": word + " "}
            else:
                # Stream the direct response
                # Clean any accidental TOOL_CALL remnants
                clean_content = re.sub(r'TOOL_CALL:.*?(?:\n|$)', '', content, flags=re.IGNORECASE).strip()
                clean_content = re.sub(r'MEMORY_SEARCH:.*?(?:\n|$)', '', clean_content, flags=re.IGNORECASE).strip()

                if clean_content:
                    # Stream via the streaming LLM for natural token flow
                    stream_messages = list(full_messages) + list(history_messages)

                    llm_stream = LLMProvider.get(
                        model=config.model,
                        temperature=config.temperature,
                        streaming=True,
                    )

                    try:
                        async for chunk in llm_stream.astream(stream_messages):
                            token = chunk.content
                            if token:
                                yield {"type": "token", "content": token}
                    except Exception:
                        for word in clean_content.split():
                            yield {"type": "token", "content": word + " "}

            yield {"type": "end", "content": ""}
            return

        # Max iterations
        yield {"type": "token", "content": "I need more information to help you. Could you rephrase?"}
        yield {"type": "end", "content": ""}