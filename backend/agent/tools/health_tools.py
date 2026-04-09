"""
Health-specific tools.
"""


def bmi_calculator(input_str: str) -> str:
    """
    Calculate Body Mass Index.
    Input format: 'weight_kg,height_m' (e.g., '75,1.80')
    """
    try:
        parts = input_str.split(",")
        weight = float(parts[0].strip())
        height = float(parts[1].strip())

        if weight <= 0 or height <= 0:
            return "Error: Weight and height must be positive numbers"

        bmi = weight / (height ** 2)

        if bmi < 16:
            category = "Severely Underweight"
            advice = "Please consult a healthcare provider immediately."
        elif bmi < 18.5:
            category = "Underweight"
            advice = "Consider consulting a nutritionist for a healthy weight gain plan."
        elif bmi < 25:
            category = "Normal Weight"
            advice = "Great! Maintain your healthy lifestyle."
        elif bmi < 30:
            category = "Overweight"
            advice = "Consider a balanced diet and regular exercise."
        elif bmi < 35:
            category = "Obese (Class I)"
            advice = "Please consult a healthcare provider for guidance."
        elif bmi < 40:
            category = "Obese (Class II)"
            advice = "Medical consultation is recommended."
        else:
            category = "Obese (Class III)"
            advice = "Please seek medical attention promptly."

        return (
            f"BMI Calculation:\n"
            f"  Weight: {weight} kg\n"
            f"  Height: {height} m\n"
            f"  BMI: {bmi:.1f}\n"
            f"  Category: {category}\n"
            f"  Note: {advice}\n"
            f"  ⚠️ BMI is a screening tool, not a diagnostic measure."
        )
    except (ValueError, IndexError):
        return "Error: Please provide input as 'weight_kg,height_m' (e.g., '75,1.80')"


def calorie_estimator(input_str: str) -> str:
    """
    Estimate daily calorie needs using Mifflin-St Jeor equation.
    Input format: 'weight_kg,height_cm,age,gender,activity_level'
    Gender: 'male' or 'female'
    Activity levels: 'sedentary', 'light', 'moderate', 'active', 'very_active'
    Example: '75,180,30,male,moderate'
    """
    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9,
    }

    try:
        parts = [p.strip().lower() for p in input_str.split(",")]
        if len(parts) != 5:
            return (
                "Error: Format should be 'weight_kg,height_cm,age,gender,activity_level'\n"
                "Example: '75,180,30,male,moderate'\n"
                "Activity levels: sedentary, light, moderate, active, very_active"
            )

        weight = float(parts[0])
        height = float(parts[1])
        age = int(parts[2])
        gender = parts[3]
        activity = parts[4]

        if gender not in ("male", "female"):
            return "Error: Gender must be 'male' or 'female'"
        if activity not in activity_multipliers:
            return f"Error: Activity must be one of: {', '.join(activity_multipliers.keys())}"

        # Mifflin-St Jeor Equation
        if gender == "male":
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

        tdee = bmr * activity_multipliers[activity]

        return (
            f"Daily Calorie Estimate:\n"
            f"  BMR (Base Metabolic Rate): {bmr:.0f} cal/day\n"
            f"  TDEE (Total Daily Energy): {tdee:.0f} cal/day\n"
            f"  Activity Level: {activity}\n\n"
            f"  For weight loss: ~{tdee - 500:.0f} cal/day\n"
            f"  For maintenance: ~{tdee:.0f} cal/day\n"
            f"  For weight gain: ~{tdee + 500:.0f} cal/day\n"
            f"  ⚠️ This is an estimate. Consult a nutritionist for personalized advice."
        )
    except (ValueError, IndexError) as e:
        return f"Error parsing input: {str(e)}"


def water_intake_calculator(input_str: str) -> str:
    """
    Calculate recommended daily water intake.
    Input format: 'weight_kg,activity_level'
    Activity: 'sedentary', 'moderate', 'active', 'athlete'
    Example: '75,moderate'
    """
    try:
        parts = [p.strip().lower() for p in input_str.split(",")]
        if len(parts) != 2:
            return "Error: Format should be 'weight_kg,activity_level' (e.g., '75,moderate')"

        weight = float(parts[0])
        activity = parts[1]

        # Base: 30-35ml per kg
        base_ml = weight * 33

        multipliers = {
            "sedentary": 1.0,
            "moderate": 1.2,
            "active": 1.4,
            "athlete": 1.6,
        }

        if activity not in multipliers:
            return f"Error: Activity must be one of: {', '.join(multipliers.keys())}"

        total_ml = base_ml * multipliers[activity]
        total_liters = total_ml / 1000
        glasses = total_ml / 250  # Standard glass = 250ml

        return (
            f"Daily Water Intake Recommendation:\n"
            f"  Weight: {weight} kg\n"
            f"  Activity: {activity}\n"
            f"  Recommended: {total_ml:.0f} ml ({total_liters:.1f} liters)\n"
            f"  That's about {glasses:.0f} glasses (250ml each)\n"
            f"  💡 Drink more in hot weather or during exercise"
        )
    except (ValueError, IndexError):
        return "Error: Format should be 'weight_kg,activity_level' (e.g., '75,moderate')"


def heart_rate_zones(input_str: str) -> str:
    """
    Calculate heart rate training zones.
    Input format: 'age' or 'age,resting_hr'
    Example: '30' or '30,60'
    """
    try:
        parts = [p.strip() for p in input_str.split(",")]
        age = int(parts[0])
        resting_hr = int(parts[1]) if len(parts) > 1 else None

        max_hr = 220 - age

        if resting_hr:
            # Karvonen formula (more accurate with resting HR)
            hr_reserve = max_hr - resting_hr
            zones = {
                "Zone 1 (Recovery)": (0.50, 0.60),
                "Zone 2 (Aerobic)": (0.60, 0.70),
                "Zone 3 (Tempo)": (0.70, 0.80),
                "Zone 4 (Threshold)": (0.80, 0.90),
                "Zone 5 (Maximum)": (0.90, 1.00),
            }
            zone_text = []
            for name, (low, high) in zones.items():
                low_hr = int(resting_hr + (hr_reserve * low))
                high_hr = int(resting_hr + (hr_reserve * high))
                zone_text.append(f"  {name}: {low_hr}-{high_hr} bpm")

            method = "Karvonen (with resting HR)"
        else:
            zones = {
                "Zone 1 (Recovery)": (0.50, 0.60),
                "Zone 2 (Aerobic)": (0.60, 0.70),
                "Zone 3 (Tempo)": (0.70, 0.80),
                "Zone 4 (Threshold)": (0.80, 0.90),
                "Zone 5 (Maximum)": (0.90, 1.00),
            }
            zone_text = []
            for name, (low, high) in zones.items():
                low_hr = int(max_hr * low)
                high_hr = int(max_hr * high)
                zone_text.append(f"  {name}: {low_hr}-{high_hr} bpm")

            method = "Standard (% of max HR)"

        zones_output = "\n".join(zone_text)
        resting_info = f"\n  Resting HR: {resting_hr} bpm" if resting_hr else ""

        return (
            f"Heart Rate Training Zones:\n"
            f"  Age: {age}\n"
            f"  Max HR: {max_hr} bpm{resting_info}\n"
            f"  Method: {method}\n\n"
            f"{zones_output}"
        )
    except (ValueError, IndexError):
        return "Error: Format should be 'age' or 'age,resting_hr' (e.g., '30' or '30,60')"