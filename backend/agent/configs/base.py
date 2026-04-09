"""
Base agent configuration schema.
Every agent 'brain' must conform to this structure.
Enhanced with validation, persona system, and response formatting.
"""

from dataclasses import dataclass, field
from typing import Callable, Optional, Any
from enum import Enum


class ResponseStyle(Enum):
    """How the agent formats its responses."""
    CONCISE = "concise"
    DETAILED = "detailed"
    CONVERSATIONAL = "conversational"
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"


@dataclass
class ToolConfig:
    """Definition of a single tool available to the agent."""
    name: str
    description: str
    function: Callable
    parameters: dict = field(default_factory=dict)
    examples: list[str] = field(default_factory=list)
    category: str = "general"

    def get_full_description(self) -> str:
        """Get description with examples for better LLM understanding."""
        desc = f"{self.name}: {self.description}"
        if self.parameters:
            params = ", ".join(f"{k}: {v}" for k, v in self.parameters.items())
            desc += f"\n  Parameters: {params}"
        if self.examples:
            examples_text = "\n  ".join(f"Example: {e}" for e in self.examples)
            desc += f"\n  {examples_text}"
        return desc


@dataclass
class MemoryConfig:
    """Memory strategy configuration."""
    short_term_limit: int = 10
    long_term_enabled: bool = True
    long_term_top_k: int = 3
    auto_store: bool = True
    store_threshold: float = 0.5  # Min importance score to auto-store
    memory_categories: list[str] = field(default_factory=lambda: ["general"])


@dataclass
class PersonaConfig:
    """Agent personality and behavior traits."""
    name: str = "Assistant"
    role: str = "AI Assistant"
    tone: str = "helpful and professional"
    emoji_usage: bool = False
    response_style: ResponseStyle = ResponseStyle.CONVERSATIONAL
    greeting: str = "Hello! How can I help you today?"
    farewell: str = "Goodbye! Feel free to come back anytime."
    error_message: str = "I'm sorry, I encountered an issue. Could you rephrase that?"
    thinking_phrases: list[str] = field(default_factory=lambda: [
        "Let me think about that...",
        "Good question!",
        "Here's what I know...",
    ])


@dataclass
class GuardrailConfig:
    """Safety and behavioral guardrails."""
    blocked_topics: list[str] = field(default_factory=list)
    max_response_length: int = 2000
    require_citations: bool = False
    disclaimer_text: Optional[str] = None
    content_filter: bool = True
    allowed_languages: list[str] = field(default_factory=lambda: ["english"])


@dataclass
class AgentConfig:
    """
    Complete agent configuration — the 'brain'.

    This is what gets swapped to change agent behavior
    without modifying any core infrastructure.
    """
    name: str
    description: str
    system_prompt: str
    tools: list[ToolConfig] = field(default_factory=list)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    persona: PersonaConfig = field(default_factory=PersonaConfig)
    guardrails: GuardrailConfig = field(default_factory=GuardrailConfig)
    constraints: list[str] = field(default_factory=list)
    max_iterations: int = 5
    temperature: float = 0.7
    model: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    version: str = "1.0.0"

    def build_system_prompt(self) -> str:
        """
        Build the complete system prompt by combining all config elements.
        This is the master prompt sent to the LLM.
        """
        sections = []

        # Core identity
        sections.append(f"# Role: {self.persona.role}")
        sections.append(f"# Name: {self.persona.name}")
        sections.append(f"# Tone: {self.persona.tone}")
        sections.append("")

        # Main system prompt
        sections.append(self.system_prompt)
        sections.append("")

        # Response style guidance
        style_guide = self._get_style_guide()
        if style_guide:
            sections.append(f"## Response Style\n{style_guide}")
            sections.append("")

        # Constraints
        if self.constraints:
            constraints_text = "\n".join(f"- {c}" for c in self.constraints)
            sections.append(f"## Rules & Constraints\n{constraints_text}")
            sections.append("")

        # Guardrails
        guardrail_text = self._get_guardrail_text()
        if guardrail_text:
            sections.append(f"## Safety Guidelines\n{guardrail_text}")
            sections.append("")

        # Disclaimer
        if self.guardrails.disclaimer_text:
            sections.append(
                f"## Important Disclaimer\n"
                f"Always include this when relevant: {self.guardrails.disclaimer_text}"
            )
            sections.append("")

        return "\n".join(sections)

    def _get_style_guide(self) -> str:
        """Get response style instructions."""
        style_map = {
            ResponseStyle.CONCISE: (
                "Keep responses brief and to the point. "
                "Use bullet points when listing items. "
                "Avoid unnecessary elaboration."
            ),
            ResponseStyle.DETAILED: (
                "Provide thorough, comprehensive responses. "
                "Include relevant details, examples, and explanations. "
                "Structure responses with clear sections when appropriate."
            ),
            ResponseStyle.CONVERSATIONAL: (
                "Respond in a natural, conversational manner. "
                "Be engaging and approachable. "
                "Balance detail with readability."
            ),
            ResponseStyle.PROFESSIONAL: (
                "Maintain a professional, authoritative tone. "
                "Use proper terminology. "
                "Structure responses clearly with evidence-based information."
            ),
            ResponseStyle.FRIENDLY: (
                "Be warm, encouraging, and supportive. "
                "Use a friendly tone. "
                "Make complex topics feel accessible and fun."
            ),
        }
        text = style_map.get(self.persona.response_style, "")
        if self.persona.emoji_usage:
            text += " Use relevant emojis to make responses more engaging."
        return text

    def _get_guardrail_text(self) -> str:
        """Get guardrail instructions."""
        lines = []
        if self.guardrails.blocked_topics:
            topics = ", ".join(self.guardrails.blocked_topics)
            lines.append(f"- Do NOT discuss: {topics}")
        if self.guardrails.require_citations:
            lines.append("- Cite sources when making factual claims")
        if self.guardrails.content_filter:
            lines.append("- Avoid harmful, offensive, or inappropriate content")
        lines.append(
            f"- Keep responses under {self.guardrails.max_response_length} characters when possible"
        )
        return "\n".join(lines)

    def get_tool_descriptions(self) -> str:
        """Format tool descriptions for the LLM prompt."""
        if not self.tools:
            return "No tools available."
        return "\n".join(
            f"- {tool.get_full_description()}" for tool in self.tools
        )

    def get_tool_names(self) -> list[str]:
        """Get list of available tool names."""
        return [t.name for t in self.tools]

    def get_tool_by_name(self, name: str) -> Optional[ToolConfig]:
        """Look up a tool by name."""
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None

    def get_tools_by_category(self, category: str) -> list[ToolConfig]:
        """Get tools filtered by category."""
        return [t for t in self.tools if t.category == category]

    def validate(self) -> list[str]:
        """Validate the config and return any issues."""
        issues = []
        if not self.name:
            issues.append("Agent name is required")
        if not self.system_prompt:
            issues.append("System prompt is required")
        if self.max_iterations < 1:
            issues.append("max_iterations must be at least 1")
        if self.temperature < 0 or self.temperature > 2:
            issues.append("temperature must be between 0 and 2")

        # Check tool name uniqueness
        tool_names = [t.name for t in self.tools]
        if len(tool_names) != len(set(tool_names)):
            issues.append("Tool names must be unique")

        return issues