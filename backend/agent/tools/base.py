"""
Base tool interface and shared utilities.
"""

from typing import Any


def safe_execute(func, input_str: str) -> str:
    """Safely execute a tool function with error handling."""
    try:
        result = func(input_str)
        return str(result)
    except Exception as e:
        return f"Tool error: {str(e)}"


def parse_key_value_input(input_str: str) -> dict:
    """
    Parse input like 'key1=value1, key2=value2' into a dict.
    Also handles 'value1,value2' positional format.
    """
    result = {}

    if "=" in input_str:
        pairs = input_str.split(",")
        for pair in pairs:
            if "=" in pair:
                key, value = pair.split("=", 1)
                result[key.strip()] = value.strip()
    else:
        parts = [p.strip() for p in input_str.split(",")]
        for i, part in enumerate(parts):
            result[f"arg{i}"] = part

    return result