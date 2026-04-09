"""
LangGraph nodes - each function is a node in the agent graph.
Fixed: no JSON mode, robust parsing.
"""

import json
import re
import time
from typing import Any
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from agent.core.state import AgentState
from agent.core.llm_provider import LLMProvider
from agent.configs.registry import get_agent_config


def prepare_messages(state: AgentState) -> dict:
    """
    Build the full message list for the LLM.
    """
    config = get_agent_config(state["agent_type"])

    system_parts = [config.build_system_prompt()]

    if config.tools:
        tool_names = ", ".join(config.get_tool_names())
        system_parts.append(
            f"\n\nAVAILABLE TOOLS:\n{config.get_tool_descriptions()}\n\n"
            "TOOL USAGE INSTRUCTIONS:\n"
            "If you need to use a tool, write your response in this exact format:\n"
            "TOOL_CALL: tool_name | input_value\n\n"
            "If you want to search your memory for context, write:\n"
            "MEMORY_SEARCH: your search query\n\n"
            "If you have the final answer and do NOT need any tool, "
            "just write your response normally without any TOOL_CALL or MEMORY_SEARCH prefix.\n\n"
            f"Available tool names: {tool_names}\n"
            "Only use TOOL_CALL when the user explicitly needs a calculation or data lookup. "
            "For general questions, just respond directly."
        )

    if state.get("memory_context"):
        system_parts.append(
            f"\n\nRELEVANT CONTEXT FROM MEMORY:\n{state['memory_context']}\n"
            "Use this context to inform your response if relevant."
        )

    if state.get("tools_output"):
        system_parts.append(
            f"\n\nTOOL RESULT:\n{state['tools_output']}\n"
            "Use this result to formulate a helpful response to the user. "
            "Present the data clearly and add any relevant advice or context."
        )

    system_prompt = "\n".join(system_parts)
    new_messages = [SystemMessage(content=system_prompt)]

    return {"messages": new_messages}


def llm_node(state: AgentState) -> dict:
    """
    Call the LLM. Uses standard mode (no JSON mode).
    """
    config = get_agent_config(state["agent_type"])
    llm = LLMProvider.get_for_decision(
        model=config.model,
        temperature=config.temperature,
    )

    start_time = time.time()
    response = llm.invoke(state["messages"])
    latency = int((time.time() - start_time) * 1000)

    return {
        "messages": [response],
        "iteration": state["iteration"] + 1,
        "metadata": {
            **(state.get("metadata") or {}),
            "last_llm_latency_ms": latency,
        },
    }


def parse_decision(state: AgentState) -> dict:
    """
    Parse LLM response to detect tool calls, memory searches, or final responses.
    Uses pattern matching instead of JSON mode.
    """
    last_message = state["messages"][-1]
    content = last_message.content.strip()

    # Check for TOOL_CALL pattern
    tool_match = re.search(
        r'TOOL_CALL:\s*(\S+)\s*\|\s*(.+?)(?:\n|$)',
        content,
        re.IGNORECASE
    )
    if tool_match:
        tool_name = tool_match.group(1).strip()
        tool_input = tool_match.group(2).strip()
        return {
            "next_action": "tool_call",
            "tool_name": tool_name,
            "tool_input": tool_input,
        }

    # Check for MEMORY_SEARCH pattern
    memory_match = re.search(
        r'MEMORY_SEARCH:\s*(.+?)(?:\n|$)',
        content,
        re.IGNORECASE
    )
    if memory_match:
        query = memory_match.group(1).strip()
        return {
            "next_action": "memory_fetch",
            "tool_input": query,
        }

    # Also try JSON format as fallback (in case LLM outputs JSON anyway)
    try:
        parsed = json.loads(content)
        action = parsed.get("action", "respond")
        if action == "tool_call":
            return {
                "next_action": "tool_call",
                "tool_name": parsed.get("tool", ""),
                "tool_input": parsed.get("input", ""),
            }
        elif action == "memory_fetch":
            return {
                "next_action": "memory_fetch",
                "tool_input": parsed.get("query", ""),
            }
        else:
            return {
                "next_action": "respond",
                "final_response": parsed.get("message", content),
            }
    except (json.JSONDecodeError, AttributeError):
        pass

    # Default: treat as direct response
    return {
        "next_action": "respond",
        "final_response": content,
    }


def execute_tool(state: AgentState) -> dict:
    """Execute the tool selected by the LLM."""
    config = get_agent_config(state["agent_type"])
    tool_name = state.get("tool_name", "")
    tool_input = state.get("tool_input", "")

    tool_config = config.get_tool_by_name(tool_name)

    if not tool_config:
        return {
            "tools_output": f"Error: Tool '{tool_name}' not found. "
            f"Available tools: {config.get_tool_names()}",
            "next_action": None,
            "tool_name": None,
            "tool_input": None,
        }

    try:
        start_time = time.time()
        result = tool_config.function(tool_input)
        latency = int((time.time() - start_time) * 1000)

        return {
            "tools_output": str(result),
            "next_action": None,
            "tool_name": None,
            "tool_input": None,
            "metadata": {
                **(state.get("metadata") or {}),
                "last_tool_call": {
                    "name": tool_name,
                    "input": tool_input,
                    "latency_ms": latency,
                },
            },
        }
    except Exception as e:
        return {
            "tools_output": f"Error executing tool '{tool_name}': {str(e)}",
            "next_action": None,
            "tool_name": None,
            "tool_input": None,
        }


def memory_fetch(state: AgentState) -> dict:
    """Retrieve relevant context from long-term vector memory."""
    from memory.manager import MemoryManager

    config = get_agent_config(state["agent_type"])
    query = state.get("tool_input", "")

    if not query or not config.memory.long_term_enabled:
        return {
            "memory_context": "No relevant memory found.",
            "next_action": None,
            "tool_input": None,
        }

    try:
        results = MemoryManager.get_context(
            session_id=state.get("session_id", ""),
            user_id=state.get("user_id", "anonymous"),
            current_message=query,
            memory_config=config.memory,
        )

        memory_text = results.get("formatted", "")
        if not memory_text:
            memory_text = "No relevant memories found."

        return {
            "memory_context": memory_text,
            "next_action": None,
            "tool_input": None,
        }

    except Exception as e:
        return {
            "memory_context": f"Memory search error: {str(e)}",
            "next_action": None,
            "tool_input": None,
        }


def format_response(state: AgentState) -> dict:
    """Prepare the final response for output."""
    response = state.get("final_response", "")

    if not response:
        for msg in reversed(state["messages"]):
            if isinstance(msg, AIMessage):
                content = msg.content.strip()
                # Remove any leftover TOOL_CALL or MEMORY_SEARCH lines
                content = re.sub(r'TOOL_CALL:.*?(?:\n|$)', '', content, flags=re.IGNORECASE).strip()
                content = re.sub(r'MEMORY_SEARCH:.*?(?:\n|$)', '', content, flags=re.IGNORECASE).strip()
                if content:
                    response = content
                    break

    if not response:
        config = get_agent_config(state["agent_type"])
        response = config.persona.error_message

    return {"final_response": response}