"""
API fetcher tools — retrieve data from free public APIs.
"""

import httpx
import json
from typing import Optional


def fetch_url(input_str: str) -> str:
    """
    Fetch data from a URL (GET request).
    Input: A valid URL string.
    Returns: Response text (truncated to 1000 chars).
    """
    try:
        url = input_str.strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        with httpx.Client(timeout=10) as client:
            response = client.get(url)
            response.raise_for_status()

        text = response.text[:1000]
        return f"Response from {url}:\n{text}"

    except httpx.TimeoutException:
        return f"Error: Request to {input_str} timed out"
    except httpx.HTTPStatusError as e:
        return f"Error: HTTP {e.response.status_code} from {input_str}"
    except Exception as e:
        return f"Error fetching {input_str}: {str(e)}"


def get_random_fact(input_str: str = "") -> str:
    """
    Get a random interesting fact.
    Input: ignored (no input needed).
    """
    try:
        with httpx.Client(timeout=10) as client:
            response = client.get(
                "https://uselessfacts.jsph.pl/api/v2/facts/random",
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            data = response.json()
            return f"Fun fact: {data.get('text', 'No fact available')}"
    except Exception as e:
        return f"Could not fetch a fun fact: {str(e)}"


def get_weather_info(input_str: str) -> str:
    """
    Get current weather for a city using wttr.in (free, no API key).
    Input: City name (e.g., 'London')
    """
    try:
        city = input_str.strip()
        with httpx.Client(timeout=10) as client:
            response = client.get(
                f"https://wttr.in/{city}?format=j1",
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            data = response.json()

        current = data.get("current_condition", [{}])[0]
        location = data.get("nearest_area", [{}])[0]

        area = location.get("areaName", [{}])[0].get("value", city)
        country = location.get("country", [{}])[0].get("value", "")
        temp_c = current.get("temp_C", "?")
        temp_f = current.get("temp_F", "?")
        humidity = current.get("humidity", "?")
        desc = current.get("weatherDesc", [{}])[0].get("value", "Unknown")
        wind_kph = current.get("windspeedKmph", "?")
        feels_like = current.get("FeelsLikeC", "?")

        return (
            f"Weather in {area}, {country}:\n"
            f"  Condition: {desc}\n"
            f"  Temperature: {temp_c}°C ({temp_f}°F)\n"
            f"  Feels like: {feels_like}°C\n"
            f"  Humidity: {humidity}%\n"
            f"  Wind: {wind_kph} km/h"
        )

    except Exception as e:
        return f"Could not fetch weather for '{input_str}': {str(e)}"


def get_word_definition(input_str: str) -> str:
    """
    Look up the definition of a word using Free Dictionary API.
    Input: A single word (e.g., 'serendipity')
    """
    try:
        word = input_str.strip().lower()
        with httpx.Client(timeout=10) as client:
            response = client.get(
                f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
            )
            response.raise_for_status()
            data = response.json()

        if not data:
            return f"No definition found for '{word}'"

        entry = data[0]
        word_name = entry.get("word", word)
        phonetic = entry.get("phonetic", "")

        definitions = []
        for meaning in entry.get("meanings", [])[:3]:
            pos = meaning.get("partOfSpeech", "")
            for defn in meaning.get("definitions", [])[:2]:
                text = defn.get("definition", "")
                example = defn.get("example", "")
                line = f"  [{pos}] {text}"
                if example:
                    line += f'\n    Example: "{example}"'
                definitions.append(line)

        defs_text = "\n".join(definitions)
        return f"📖 {word_name} {phonetic}\n{defs_text}"

    except httpx.HTTPStatusError:
        return f"No definition found for '{input_str}'"
    except Exception as e:
        return f"Error looking up '{input_str}': {str(e)}"


def get_date_time_info(input_str: str) -> str:
    """
    Get current date/time info for a timezone.
    Input: Timezone area (e.g., 'America/New_York', 'Europe/London', 'Asia/Tokyo')
    """
    try:
        timezone = input_str.strip()
        with httpx.Client(timeout=10) as client:
            response = client.get(
                f"https://worldtimeapi.org/api/timezone/{timezone}"
            )
            response.raise_for_status()
            data = response.json()

        datetime_str = data.get("datetime", "Unknown")
        day_of_week = data.get("day_of_week", "")
        timezone_name = data.get("timezone", timezone)
        utc_offset = data.get("utc_offset", "")

        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_name = days[day_of_week] if isinstance(day_of_week, int) and 0 <= day_of_week <= 6 else ""

        # Parse datetime
        date_part = datetime_str.split("T")[0] if "T" in datetime_str else datetime_str
        time_part = datetime_str.split("T")[1].split(".")[0] if "T" in datetime_str else ""

        return (
            f"🕐 {timezone_name} (UTC{utc_offset})\n"
            f"  Date: {date_part} ({day_name})\n"
            f"  Time: {time_part}"
        )

    except httpx.HTTPStatusError:
        return (
            f"Unknown timezone '{input_str}'. "
            f"Use format like 'America/New_York', 'Europe/London', 'Asia/Tokyo'"
        )
    except Exception as e:
        return f"Error fetching time for '{input_str}': {str(e)}"