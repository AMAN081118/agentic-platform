"""
Health check and system info endpoints.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "agentic-ai-platform",
        "version": "0.3.0",
    }


@router.get("/agents")
async def list_agents():
    """List all registered agent types — dynamically from registry."""
    from agent.configs.registry import list_agents as get_agents
    return {"agents": get_agents()}