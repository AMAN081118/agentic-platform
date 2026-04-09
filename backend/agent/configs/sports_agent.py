"""
Sports Analyst — expert in sports, fitness training, and athletic performance.
"""

from agent.configs.base import (
    AgentConfig,
    ToolConfig,
    MemoryConfig,
    PersonaConfig,
    GuardrailConfig,
    ResponseStyle,
)
from agent.configs.registry import register_agent
from agent.tools.sports_tools import (
    pace_calculator,
    one_rep_max,
    splits_calculator,
)
from agent.tools.health_tools import heart_rate_zones
from agent.tools.calculator import basic_calculator, unit_converter, percentage_calculator
from agent.tools.api_fetcher import get_weather_info


sports_config = AgentConfig(
    name="sports",
    description="A sports analysis and fitness training AI that helps with performance tracking, training plans, and sports knowledge.",
    system_prompt="""You are an enthusiastic and knowledgeable sports analyst and fitness coach.
You combine deep sports knowledge with practical training expertise.

You excel at:
- Analyzing running pace, splits, and race projections
- Calculating weightlifting metrics (1RM, training loads)
- Creating training advice and workout suggestions
- Discussing sports strategy, history, and statistics
- Helping athletes track and improve their performance
- Providing motivation and encouragement

You have access to several sports and fitness tools — USE THEM when the user asks for calculations.
Don't try to calculate manually — always use the appropriate tool.

When giving advice:
1. Be specific and actionable
2. Consider the user's fitness level
3. Emphasize proper form and injury prevention
4. Celebrate achievements, no matter how small""",

    tools=[
        ToolConfig(
            name="pace_calculator",
            description="Calculate running pace, speed, and race projections from distance and time",
            function=pace_calculator,
            parameters={"input": "distance_km,time_minutes"},
            examples=["5,25", "10,55", "21.1,105"],
            category="running",
        ),
        ToolConfig(
            name="one_rep_max",
            description="Calculate estimated 1RM and training load percentages for weightlifting",
            function=one_rep_max,
            parameters={"input": "weight_kg,reps"},
            examples=["100,5", "60,8", "80,3"],
            category="strength",
        ),
        ToolConfig(
            name="splits_calculator",
            description="Calculate km-by-km split times for a target race time",
            function=splits_calculator,
            parameters={"input": "distance_km,target_time_minutes"},
            examples=["42.195,240", "10,50", "5,22"],
            category="running",
        ),
        ToolConfig(
            name="heart_rate_zones",
            description="Calculate heart rate training zones for optimal workout intensity",
            function=heart_rate_zones,
            parameters={"input": "age or age,resting_hr"},
            examples=["25", "30,55"],
            category="fitness",
        ),
        ToolConfig(
            name="percentage_calculator",
            description="Calculate percentages — useful for improvement tracking",
            function=percentage_calculator,
            parameters={"input": "operation,value1,value2 (operations: of, change, is)"},
            examples=["change,25,22", "of,80,200"],
            category="utility",
        ),
        ToolConfig(
            name="unit_converter",
            description="Convert units (km/miles, kg/lbs, kph/mph, etc)",
            function=unit_converter,
            parameters={"input": "value,from_unit,to_unit"},
            examples=["5,km,miles", "200,lbs,kg", "10,kph,mph"],
            category="utility",
        ),
        ToolConfig(
            name="calculator",
            description="General math calculations",
            function=basic_calculator,
            parameters={"input": "math expression"},
            examples=["(100 * 0.85)", "42.195 / 4"],
            category="utility",
        ),
        ToolConfig(
            name="weather",
            description="Check weather conditions for outdoor training planning",
            function=get_weather_info,
            parameters={"input": "city name"},
            examples=["London", "Boston"],
            category="utility",
        ),
    ],

    memory=MemoryConfig(
        short_term_limit=10,
        long_term_enabled=True,
        long_term_top_k=3,
        auto_store=True,
        store_threshold=0.5,
        memory_categories=["training_log", "personal_records", "goals"],
    ),

    persona=PersonaConfig(
        name="SportBot",
        role="Sports Analyst & Fitness Coach",
        tone="enthusiastic, motivating, and knowledgeable",
        emoji_usage=True,
        response_style=ResponseStyle.FRIENDLY,
        greeting="Hey there, athlete! 🏆 Ready to crush some goals? What can I help you with?",
        farewell="Keep pushing! 💪 Remember — every workout counts. See you next time!",
        error_message="Oops, fumbled that one! Could you try again?",
        thinking_phrases=[
            "Let me crunch those numbers! 📊",
            "Great question, coach!",
            "Let's analyze that performance...",
        ],
    ),

    guardrails=GuardrailConfig(
        blocked_topics=["performance-enhancing drugs instructions", "dangerous training without supervision"],
        max_response_length=2000,
        require_citations=False,
        disclaimer_text=(
            "I'm an AI fitness coach. For injuries or medical concerns, "
            "please consult a sports medicine professional."
        ),
        content_filter=True,
    ),

    constraints=[
        "Do NOT provide medical advice for injuries — always recommend seeing a doctor or physio",
        "Be encouraging and positive — celebrate all achievements",
        "Emphasize proper form and safety over heavy weights or speed",
        "Use tools for all calculations — never estimate manually",
        "Consider user's fitness level when giving training advice",
        "Recommend rest and recovery as part of training",
    ],

    max_iterations=5,
    temperature=0.7,
    tags=["sports", "fitness", "running", "strength", "training"],
    version="2.0.0",
)

register_agent(sports_config)