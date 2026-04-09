"""
Tools registry — importable tool functions.
"""

from agent.tools.calculator import basic_calculator, unit_converter, percentage_calculator
from agent.tools.api_fetcher import (
    fetch_url,
    get_random_fact,
    get_weather_info,
    get_word_definition,
    get_date_time_info,
)
from agent.tools.health_tools import (
    bmi_calculator,
    calorie_estimator,
    water_intake_calculator,
    heart_rate_zones,
)
from agent.tools.sports_tools import (
    pace_calculator,
    one_rep_max,
    splits_calculator,
)
from agent.tools.education_tools import (
    flashcard_generator,
    study_timer,
    grade_calculator,
)

__all__ = [
    "basic_calculator",
    "unit_converter",
    "percentage_calculator",
    "fetch_url",
    "get_random_fact",
    "get_weather_info",
    "get_word_definition",
    "get_date_time_info",
    "bmi_calculator",
    "calorie_estimator",
    "water_intake_calculator",
    "heart_rate_zones",
    "pace_calculator",
    "one_rep_max",
    "splits_calculator",
    "flashcard_generator",
    "study_timer",
    "grade_calculator",
]