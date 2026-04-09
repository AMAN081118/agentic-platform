"""
Education-specific tools.
"""

import json


def flashcard_generator(input_str: str) -> str:
    """
    Generate study flashcards for a topic.
    Input: A topic or concept (e.g., 'photosynthesis')
    Returns pre-built flashcard templates.
    """
    topic = input_str.strip().lower()

    # Pre-built flashcard sets for common topics
    flashcard_db = {
        "photosynthesis": [
            ("What is photosynthesis?", "The process by which plants convert light energy into chemical energy (glucose) using CO2 and water."),
            ("What is the equation?", "6CO2 + 6H2O + light → C6H12O6 + 6O2"),
            ("Where does it occur?", "In chloroplasts, specifically in the thylakoid membranes and stroma."),
            ("What are the two stages?", "Light-dependent reactions and the Calvin cycle (light-independent)."),
            ("What pigment is key?", "Chlorophyll — it absorbs red and blue light, reflecting green."),
        ],
        "newton's laws": [
            ("First Law (Inertia)?", "An object stays at rest or in uniform motion unless acted on by an external force."),
            ("Second Law?", "F = ma — Force equals mass times acceleration."),
            ("Third Law?", "Every action has an equal and opposite reaction."),
            ("Example of 1st law?", "A book on a table stays still until pushed. A hockey puck slides until friction stops it."),
            ("Units of force?", "Newton (N) = kg⋅m/s²"),
        ],
        "python basics": [
            ("What is a variable?", "A named container that stores a value. Created with assignment: x = 5"),
            ("List vs Tuple?", "Lists are mutable (can change), tuples are immutable (fixed). List: [], Tuple: ()"),
            ("What is a function?", "A reusable block of code defined with 'def'. Example: def greet(name): return f'Hello {name}'"),
            ("What is a loop?", "Repeating code. 'for' iterates over sequences, 'while' runs until condition is false."),
            ("What is a dictionary?", "Key-value pairs: {'name': 'Alice', 'age': 25}. Access with dict['key']."),
        ],
    }

    # Find matching topic
    matched_topic = None
    for key in flashcard_db:
        if key in topic or topic in key:
            matched_topic = key
            break

    if matched_topic:
        cards = flashcard_db[matched_topic]
        output_lines = [f"📚 Flashcards: {matched_topic.title()}\n"]
        for i, (q, a) in enumerate(cards, 1):
            output_lines.append(f"Card {i}:")
            output_lines.append(f"  Q: {q}")
            output_lines.append(f"  A: {a}")
            output_lines.append("")
        return "\n".join(output_lines)
    else:
        return (
            f"I don't have pre-built flashcards for '{input_str}', "
            f"but I can help you create custom ones! "
            f"Available topics: {', '.join(flashcard_db.keys())}. "
            f"Or ask me to explain the topic and I'll generate cards from my knowledge."
        )


def study_timer(input_str: str) -> str:
    """
    Create a study schedule using the Pomodoro technique.
    Input format: 'total_hours,subject' (e.g., '3,mathematics')
    """
    try:
        parts = [p.strip() for p in input_str.split(",")]
        if len(parts) < 2:
            return "Error: Format should be 'total_hours,subject' (e.g., '3,mathematics')"

        total_hours = float(parts[0])
        subject = parts[1]

        if total_hours <= 0 or total_hours > 12:
            return "Error: Study time should be between 0.5 and 12 hours"

        total_minutes = int(total_hours * 60)

        # Pomodoro: 25 min work + 5 min break
        pomodoro_cycle = 30  # 25 + 5
        long_break_after = 4  # Long break every 4 pomodoros
        long_break_duration = 15

        sessions = []
        elapsed = 0
        pomodoro_count = 0
        session_num = 1

        while elapsed < total_minutes:
            # Work session
            work_end = elapsed + 25
            if work_end > total_minutes:
                work_end = total_minutes
            sessions.append(f"  {session_num}. 📖 Study {subject} ({elapsed}-{work_end} min)")
            elapsed = work_end
            pomodoro_count += 1
            session_num += 1

            if elapsed >= total_minutes:
                break

            # Break
            if pomodoro_count % long_break_after == 0:
                break_end = min(elapsed + long_break_duration, total_minutes)
                sessions.append(f"  ☕ Long break ({elapsed}-{break_end} min)")
                elapsed = break_end
            else:
                break_end = min(elapsed + 5, total_minutes)
                sessions.append(f"  💤 Short break ({elapsed}-{break_end} min)")
                elapsed = break_end

        schedule = "\n".join(sessions)

        return (
            f"📅 Study Plan: {subject.title()}\n"
            f"  Total time: {total_hours} hours ({total_minutes} min)\n"
            f"  Method: Pomodoro Technique\n"
            f"  Pomodoros: {pomodoro_count}\n\n"
            f"  Schedule:\n{schedule}\n\n"
            f"  💡 Tips:\n"
            f"  - Remove distractions during study blocks\n"
            f"  - Review notes at the start of each pomodoro\n"
            f"  - Use breaks to move around and hydrate"
        )
    except (ValueError, IndexError):
        return "Error: Format should be 'total_hours,subject' (e.g., '3,mathematics')"


def grade_calculator(input_str: str) -> str:
    """
    Calculate weighted grade average.
    Input format: 'score1:weight1,score2:weight2,...' (e.g., '85:30,90:30,78:40')
    Scores out of 100, weights as percentages.
    """
    try:
        pairs = [p.strip() for p in input_str.split(",")]
        total_weighted = 0
        total_weight = 0
        details = []

        for i, pair in enumerate(pairs, 1):
            parts = pair.split(":")
            if len(parts) != 2:
                return f"Error: Each entry should be 'score:weight'. Problem at entry {i}: '{pair}'"

            score = float(parts[0])
            weight = float(parts[1])

            if score < 0 or score > 100:
                return f"Error: Scores must be 0-100. Got {score} at entry {i}"

            total_weighted += score * weight
            total_weight += weight
            details.append(f"  Assignment {i}: {score}/100 (weight: {weight}%)")

        if total_weight == 0:
            return "Error: Total weight cannot be 0"

        average = total_weighted / total_weight

        # Letter grade
        if average >= 93:
            letter = "A"
        elif average >= 90:
            letter = "A-"
        elif average >= 87:
            letter = "B+"
        elif average >= 83:
            letter = "B"
        elif average >= 80:
            letter = "B-"
        elif average >= 77:
            letter = "C+"
        elif average >= 73:
            letter = "C"
        elif average >= 70:
            letter = "C-"
        elif average >= 67:
            letter = "D+"
        elif average >= 60:
            letter = "D"
        else:
            letter = "F"

        details_text = "\n".join(details)
        weight_note = "" if abs(total_weight - 100) < 0.01 else f"\n  ⚠️ Weights sum to {total_weight}%, not 100%"

        return (
            f"Grade Report:\n{details_text}\n\n"
            f"  Weighted Average: {average:.1f}/100\n"
            f"  Letter Grade: {letter}\n"
            f"  Total Weight: {total_weight}%{weight_note}"
        )
    except (ValueError, IndexError):
        return "Error: Format should be 'score1:weight1,score2:weight2' (e.g., '85:30,90:30,78:40')"