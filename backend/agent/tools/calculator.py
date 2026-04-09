"""
Calculator tools — math operations.
"""

import math


def basic_calculator(input_str: str) -> str:
    """
    Evaluate a mathematical expression safely.
    Supports: +, -, *, /, **, sqrt, sin, cos, tan, log, pi, e
    Input: A math expression as a string (e.g., '(15 * 3) + sqrt(144)')
    """
    try:
        # Safe math namespace
        safe_dict = {
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum,
            "pow": pow,
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log,
            "log10": math.log10,
            "log2": math.log2,
            "pi": math.pi,
            "e": math.e,
            "ceil": math.ceil,
            "floor": math.floor,
        }

        # Clean input
        expression = input_str.strip()

        # Basic validation — block dangerous operations
        blocked = ["import", "exec", "eval", "open", "__", "os", "sys"]
        for word in blocked:
            if word in expression.lower():
                return f"Error: '{word}' is not allowed in expressions"

        result = eval(expression, {"__builtins__": {}}, safe_dict)
        return f"Result: {result}"

    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception as e:
        return f"Error calculating '{input_str}': {str(e)}"


def unit_converter(input_str: str) -> str:
    """
    Convert between common units.
    Input format: 'value,from_unit,to_unit' (e.g., '100,kg,lbs')
    """
    conversions = {
        ("kg", "lbs"): lambda x: x * 2.20462,
        ("lbs", "kg"): lambda x: x / 2.20462,
        ("km", "miles"): lambda x: x * 0.621371,
        ("miles", "km"): lambda x: x / 0.621371,
        ("m", "ft"): lambda x: x * 3.28084,
        ("ft", "m"): lambda x: x / 3.28084,
        ("cm", "inches"): lambda x: x * 0.393701,
        ("inches", "cm"): lambda x: x / 0.393701,
        ("celsius", "fahrenheit"): lambda x: (x * 9 / 5) + 32,
        ("fahrenheit", "celsius"): lambda x: (x - 32) * 5 / 9,
        ("c", "f"): lambda x: (x * 9 / 5) + 32,
        ("f", "c"): lambda x: (x - 32) * 5 / 9,
        ("liters", "gallons"): lambda x: x * 0.264172,
        ("gallons", "liters"): lambda x: x / 0.264172,
        ("kph", "mph"): lambda x: x * 0.621371,
        ("mph", "kph"): lambda x: x / 0.621371,
    }

    try:
        parts = [p.strip().lower() for p in input_str.split(",")]
        if len(parts) != 3:
            return "Error: Format should be 'value,from_unit,to_unit' (e.g., '100,kg,lbs')"

        value = float(parts[0])
        from_unit = parts[1]
        to_unit = parts[2]

        key = (from_unit, to_unit)
        if key not in conversions:
            available = ", ".join(f"{a}→{b}" for a, b in conversions.keys())
            return f"Error: Conversion '{from_unit}→{to_unit}' not supported. Available: {available}"

        result = conversions[key](value)
        return f"{value} {from_unit} = {result:.4f} {to_unit}"

    except ValueError:
        return "Error: First value must be a number"
    except Exception as e:
        return f"Error: {str(e)}"


def percentage_calculator(input_str: str) -> str:
    """
    Calculate percentages.
    Input format: 'operation,value1,value2'
    Operations: 'of' (X% of Y), 'change' (% change from X to Y), 'is' (X is what % of Y)
    """
    try:
        parts = [p.strip().lower() for p in input_str.split(",")]
        if len(parts) != 3:
            return (
                "Error: Format 'operation,value1,value2'. "
                "Operations: 'of' (X% of Y), 'change' (from X to Y), 'is' (X is ?% of Y)"
            )

        operation = parts[0]
        v1 = float(parts[1])
        v2 = float(parts[2])

        if operation == "of":
            result = (v1 / 100) * v2
            return f"{v1}% of {v2} = {result:.2f}"
        elif operation == "change":
            if v1 == 0:
                return "Error: Cannot calculate % change from 0"
            result = ((v2 - v1) / abs(v1)) * 100
            direction = "increase" if result > 0 else "decrease"
            return f"Change from {v1} to {v2} = {abs(result):.2f}% {direction}"
        elif operation == "is":
            if v2 == 0:
                return "Error: Cannot divide by 0"
            result = (v1 / v2) * 100
            return f"{v1} is {result:.2f}% of {v2}"
        else:
            return "Error: Operation must be 'of', 'change', or 'is'"

    except ValueError:
        return "Error: Values must be numbers"
    except Exception as e:
        return f"Error: {str(e)}"