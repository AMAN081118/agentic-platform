"""
Sports-specific tools.
"""


def pace_calculator(input_str: str) -> str:
    """
    Calculate running pace and splits.
    Input format: 'distance_km,time_minutes' (e.g., '5,25')
    """
    try:
        parts = input_str.split(",")
        distance = float(parts[0].strip())
        time_min = float(parts[1].strip())

        if distance <= 0 or time_min <= 0:
            return "Error: Distance and time must be positive numbers"

        pace = time_min / distance
        pace_min = int(pace)
        pace_sec = int((pace - pace_min) * 60)
        speed_kmh = (distance / time_min) * 60
        speed_mph = speed_kmh * 0.621371

        # Estimate race times based on this pace
        race_distances = {
            "1 km": 1,
            "5 km": 5,
            "10 km": 10,
            "Half Marathon": 21.0975,
            "Marathon": 42.195,
        }

        projections = []
        for name, dist in race_distances.items():
            proj_time = pace * dist
            hours = int(proj_time // 60)
            minutes = int(proj_time % 60)
            seconds = int((proj_time % 1) * 60)
            if hours > 0:
                projections.append(f"  {name}: {hours}:{minutes:02d}:{seconds:02d}")
            else:
                projections.append(f"  {name}: {minutes}:{seconds:02d}")

        proj_text = "\n".join(projections)

        return (
            f"Running Analysis:\n"
            f"  Distance: {distance} km\n"
            f"  Time: {time_min} min\n"
            f"  Pace: {pace_min}:{pace_sec:02d} min/km\n"
            f"  Speed: {speed_kmh:.1f} km/h ({speed_mph:.1f} mph)\n\n"
            f"  Race Projections (at same pace):\n{proj_text}"
        )
    except (ValueError, IndexError):
        return "Error: Format should be 'distance_km,time_minutes' (e.g., '5,25')"


def one_rep_max(input_str: str) -> str:
    """
    Calculate estimated one-rep max (1RM) for weightlifting.
    Input format: 'weight,reps' (e.g., '100,5')
    Uses Epley formula.
    """
    try:
        parts = input_str.split(",")
        weight = float(parts[0].strip())
        reps = int(parts[1].strip())

        if weight <= 0 or reps <= 0:
            return "Error: Weight and reps must be positive"
        if reps > 30:
            return "Error: Formula is less accurate above 30 reps"

        if reps == 1:
            orm = weight
        else:
            # Epley formula
            orm = weight * (1 + reps / 30)

        percentages = {
            "100% (1RM)": 1.00,
            "95% (2 reps)": 0.95,
            "90% (3-4 reps)": 0.90,
            "85% (5-6 reps)": 0.85,
            "80% (7-8 reps)": 0.80,
            "75% (9-10 reps)": 0.75,
            "70% (11-12 reps)": 0.70,
            "65% (13-15 reps)": 0.65,
        }

        table = []
        for label, pct in percentages.items():
            table.append(f"  {label}: {orm * pct:.1f} kg")

        table_text = "\n".join(table)

        return (
            f"One-Rep Max Estimate:\n"
            f"  Lifted: {weight} kg × {reps} reps\n"
            f"  Estimated 1RM: {orm:.1f} kg ({orm * 2.20462:.1f} lbs)\n\n"
            f"  Training Load Chart:\n{table_text}"
        )
    except (ValueError, IndexError):
        return "Error: Format should be 'weight_kg,reps' (e.g., '100,5')"


def splits_calculator(input_str: str) -> str:
    """
    Calculate split times for a target race time.
    Input format: 'distance_km,target_time_minutes' (e.g., '42.195,240')
    """
    try:
        parts = input_str.split(",")
        total_distance = float(parts[0].strip())
        total_time = float(parts[1].strip())

        if total_distance <= 0 or total_time <= 0:
            return "Error: Distance and time must be positive"

        pace = total_time / total_distance
        splits = []

        km = 1
        while km <= total_distance:
            split_time = pace * km
            hours = int(split_time // 60)
            minutes = int(split_time % 60)
            seconds = int((split_time % 1) * 60)

            if hours > 0:
                time_str = f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                time_str = f"{minutes}:{seconds:02d}"

            splits.append(f"  Km {km}: {time_str}")
            km += 1

        # Add final distance if not whole number
        if total_distance % 1 != 0:
            final_time = total_time
            hours = int(final_time // 60)
            minutes = int(final_time % 60)
            seconds = int((final_time % 1) * 60)
            if hours > 0:
                time_str = f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                time_str = f"{minutes}:{seconds:02d}"
            splits.append(f"  Km {total_distance}: {time_str} (FINISH)")

        # Limit output
        if len(splits) > 15:
            shown = splits[:5] + ["  ..."] + splits[-5:]
        else:
            shown = splits

        pace_min = int(pace)
        pace_sec = int((pace - pace_min) * 60)

        return (
            f"Split Times:\n"
            f"  Distance: {total_distance} km\n"
            f"  Target: {total_time:.0f} min\n"
            f"  Pace: {pace_min}:{pace_sec:02d} min/km\n\n"
            + "\n".join(shown)
        )
    except (ValueError, IndexError):
        return "Error: Format 'distance_km,target_time_minutes' (e.g., '42.195,240')"