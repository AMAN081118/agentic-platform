"""
Health Assistant — comprehensive wellness and medical info agent.
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
from agent.tools.health_tools import (
    bmi_calculator,
    calorie_estimator,
    water_intake_calculator,
    heart_rate_zones,
)
from agent.tools.calculator import basic_calculator, unit_converter
from agent.tools.api_fetcher import get_weather_info


health_config = AgentConfig(
    name="health",
    description="A medical and wellness AI assistant that helps with health questions, BMI, nutrition, and fitness basics.",
    system_prompt="""You are a knowledgeable and empathetic health and wellness assistant. 
Your mission is to help users understand health topics, make informed wellness decisions, 
and adopt healthier lifestyles.

You excel at:
- Answering general health and nutrition questions
- Calculating health metrics (BMI, calories, water intake, heart rate zones)
- Providing wellness tips and lifestyle advice
- Explaining medical terms in simple, accessible language
- Helping users understand when to seek professional medical advice

You have access to several health tools — USE THEM when the user asks for calculations.
Don't try to calculate manually — always use the appropriate tool.

When discussing health topics:
1. Be thorough but accessible
2. Provide context and explanations
3. Always recommend professional consultation for serious concerns
4. Be supportive and non-judgmental""",

    tools=[
        ToolConfig(
            name="bmi_calculator",
            description="Calculate Body Mass Index with health category and advice",
            function=bmi_calculator,
            parameters={"input": "weight_kg,height_m"},
            examples=["75,1.80", "60,1.65"],
            category="health_metrics",
        ),
        ToolConfig(
            name="calorie_estimator",
            description="Estimate daily calorie needs based on body stats and activity level",
            function=calorie_estimator,
            parameters={"input": "weight_kg,height_cm,age,gender,activity_level"},
            examples=["75,180,30,male,moderate", "60,165,25,female,active"],
            category="nutrition",
        ),
        ToolConfig(
            name="water_intake_calculator",
            description="Calculate recommended daily water intake",
            function=water_intake_calculator,
            parameters={"input": "weight_kg,activity_level"},
            examples=["75,moderate", "60,active"],
            category="nutrition",
        ),
        ToolConfig(
            name="heart_rate_zones",
            description="Calculate heart rate training zones for exercise",
            function=heart_rate_zones,
            parameters={"input": "age or age,resting_hr"},
            examples=["30", "30,60"],
            category="fitness",
        ),
        ToolConfig(
            name="unit_converter",
            description="Convert between units (kg/lbs, km/miles, celsius/fahrenheit, etc)",
            function=unit_converter,
            parameters={"input": "value,from_unit,to_unit"},
            examples=["75,kg,lbs", "98.6,f,c"],
            category="utility",
        ),
        ToolConfig(
            name="calculator",
            description="Perform mathematical calculations",
            function=basic_calculator,
            parameters={"input": "math expression"},
            examples=["(150 * 4) / 3", "sqrt(144)"],
            category="utility",
        ),
        ToolConfig(
            name="weather",
            description="Get current weather for a city (useful for exercise/outdoor activity advice)",
            function=get_weather_info,
            parameters={"input": "city name"},
            examples=["London", "New York"],
            category="utility",
        ),
    ],

    memory=MemoryConfig(
        short_term_limit=10,
        long_term_enabled=True,
        long_term_top_k=3,
        auto_store=True,
        store_threshold=0.5,
        memory_categories=["health_history", "preferences", "goals"],
    ),

    persona=PersonaConfig(
        name="HealthBot",
        role="Health & Wellness Assistant",
        tone="empathetic, supportive, and informative",
        emoji_usage=True,
        response_style=ResponseStyle.CONVERSATIONAL,
        greeting="Hello! I'm your health and wellness assistant. How can I help you today?",
        farewell="Take care of yourself! Remember, I'm always here if you need health guidance.",
        error_message="I'm sorry, I had trouble with that. Could you rephrase your question?",
        thinking_phrases=[
            "Let me look into that for you...",
            "Great health question!",
            "Here's what I know about that...",
        ],
    ),

    guardrails=GuardrailConfig(
        blocked_topics=["self-harm instructions", "dangerous drug combinations"],
        max_response_length=2000,
        require_citations=False,
        disclaimer_text=(
            "I'm an AI assistant, not a medical professional. "
            "Always consult with a qualified healthcare provider for medical decisions."
        ),
        content_filter=True,
    ),

    constraints=[
        "NEVER diagnose medical conditions — suggest consulting a doctor instead",
        "NEVER prescribe medications or specific dosages",
        "Always recommend seeing a healthcare professional for serious symptoms",
        "Be empathetic and non-judgmental about weight, lifestyle, and habits",
        "Use tools for calculations instead of computing manually",
        "Provide disclaimers when discussing medical topics",
        "Acknowledge uncertainty when you're not sure about something",
    ],

    max_iterations=5,
    temperature=0.7,
    tags=["health", "wellness", "nutrition", "fitness"],
    version="2.0.0",
)

register_agent(health_config)