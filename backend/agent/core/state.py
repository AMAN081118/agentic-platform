"""
Agent state — the shared data structure flowing through the LangGraph graph.
This is the 'nervous system' of the agent.
"""

from typing import TypedDict, Annotated, Sequence, Optional, Any
from langchain_core.messages import BaseMessage
import operator


class AgentState(TypedDict):
    """
    State that flows through every node in the agent graph.

    messages: The conversation history (LangChain message objects)
    agent_type: Which agent config to use (e.g., 'health', 'sports')
    session_id: Current chat session ID
    user_id: Current user ID
    tools_output: Result from the most recent tool call
    memory_context: Retrieved long-term memory snippets
    next_action: Decision from router ('respond', 'tool_call', 'memory_fetch')
    tool_name: Name of the tool to call
    tool_input: Input for the tool
    final_response: The completed response to send back
    iteration: Loop counter to prevent infinite loops
    metadata: Any extra data
    """
    messages: Annotated[Sequence[BaseMessage], operator.add]
    agent_type: str
    session_id: str
    user_id: str
    tools_output: Optional[str]
    memory_context: Optional[str]
    next_action: Optional[str]
    tool_name: Optional[str]
    tool_input: Optional[str]
    final_response: Optional[str]
    iteration: int
    metadata: Optional[dict]