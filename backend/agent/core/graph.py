"""
LangGraph agent graph builder.
This is the 'skeleton' — the reusable structure that all agents share.
"""

from langgraph.graph import StateGraph, END
from agent.core.state import AgentState
from agent.core.nodes import (
    prepare_messages,
    llm_node,
    parse_decision,
    execute_tool,
    memory_fetch,
    format_response,
)
from agent.configs.registry import get_agent_config


def route_decision(state: AgentState) -> str:
    """
    Conditional edge: routes based on the LLM's parsed decision.
    Also enforces max iteration limit to prevent infinite loops.
    """
    config = get_agent_config(state["agent_type"])

    # Safety: max iterations
    if state["iteration"] >= config.max_iterations:
        return "respond"

    action = state.get("next_action", "respond")

    if action == "tool_call":
        # Verify tool exists
        tool_name = state.get("tool_name", "")
        if config.get_tool_by_name(tool_name):
            return "tool_call"
        else:
            return "respond"
    elif action == "memory_fetch":
        if config.memory.long_term_enabled:
            return "memory_fetch"
        else:
            return "respond"
    else:
        return "respond"


def build_agent_graph() -> StateGraph:
    """
    Build the core agent graph.
    This graph is REUSABLE — behavior changes based on AgentState.agent_type.

    Flow:
        prepare_messages → llm_node → parse_decision
            → [respond]      → format_response → END
            → [tool_call]    → execute_tool → prepare_messages (loop)
            → [memory_fetch] → memory_fetch → prepare_messages (loop)
    """

    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("prepare_messages", prepare_messages)
    graph.add_node("llm_node", llm_node)
    graph.add_node("parse_decision", parse_decision)
    graph.add_node("execute_tool", execute_tool)
    graph.add_node("memory_fetch", memory_fetch)
    graph.add_node("format_response", format_response)

    # Set entry point
    graph.set_entry_point("prepare_messages")

    # Linear edges
    graph.add_edge("prepare_messages", "llm_node")
    graph.add_edge("llm_node", "parse_decision")

    # Conditional routing after decision
    graph.add_conditional_edges(
        "parse_decision",
        route_decision,
        {
            "respond": "format_response",
            "tool_call": "execute_tool",
            "memory_fetch": "memory_fetch",
        },
    )

    # Loop back edges (tool/memory → re-enter LLM)
    graph.add_edge("execute_tool", "prepare_messages")
    graph.add_edge("memory_fetch", "prepare_messages")

    # Terminal edge
    graph.add_edge("format_response", END)

    return graph


# Compiled graph — singleton
_compiled_graph = None


def get_agent_graph():
    """Get or create the compiled agent graph (singleton)."""
    global _compiled_graph
    if _compiled_graph is None:
        graph = build_agent_graph()
        _compiled_graph = graph.compile()
        print("✅ Agent graph compiled")
    return _compiled_graph