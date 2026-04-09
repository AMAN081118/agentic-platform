"""
Agent configuration registry.
Central place to register and retrieve agent configs.
"""

from typing import Optional
from agent.configs.base import AgentConfig


# Registry storage
_AGENT_REGISTRY: dict[str, AgentConfig] = {}


def register_agent(config: AgentConfig) -> None:
    """Register an agent config in the registry."""
    # Validate before registering
    issues = config.validate()
    if issues:
        print(f"  ⚠️ Agent '{config.name}' has issues: {issues}")

    _AGENT_REGISTRY[config.name] = config
    print(f"  📋 Registered agent: {config.name} (v{config.version})")


def get_agent_config(name: str) -> AgentConfig:
    """
    Get an agent config by name.
    Falls back to a default config if not found.
    """
    if name in _AGENT_REGISTRY:
        return _AGENT_REGISTRY[name]

    print(f"⚠️ Agent '{name}' not found, using default")
    return AgentConfig(
        name="default",
        description="A general-purpose AI assistant",
        system_prompt=(
            "You are a helpful AI assistant. "
            "Answer questions clearly and concisely."
        ),
    )


def list_agents() -> list[dict]:
    """List all registered agents with full metadata."""
    return [
        {
            "id": name,
            "name": config.persona.name,
            "description": config.description,
            "role": config.persona.role,
            "tools": config.get_tool_names(),
            "tool_count": len(config.tools),
            "tags": config.tags,
            "version": config.version,
            "greeting": config.persona.greeting,
        }
        for name, config in _AGENT_REGISTRY.items()
    ]


def get_agent_names() -> list[str]:
    """Get just the agent ID names."""
    return list(_AGENT_REGISTRY.keys())


def load_all_agents() -> None:
    """Import all agent config modules to trigger registration."""
    print("🧠 Loading agent configs...")
    from agent.configs import health_agent    # noqa: F401
    from agent.configs import sports_agent    # noqa: F401
    from agent.configs import education_agent # noqa: F401
    print(f"✅ {len(_AGENT_REGISTRY)} agents loaded")