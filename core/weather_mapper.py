"""
Weather Mapper - Converts weathercode + is_day + modifiers to wallpaper key
"""

import logging

logger = logging.getLogger(__name__)


def get_condition_base(weathercode: int) -> str:
    """Map weathercode to a base condition string."""
    if weathercode == 0:
        return "clear"
    elif weathercode == 1:
        return "clear"
    elif weathercode == 2:
        return "partly_cloudy"
    elif weathercode == 3:
        return "cloudy"
    elif weathercode in range(45, 49):
        return "fog"
    elif weathercode in range(51, 68):
        return "rain"
    elif weathercode in range(71, 78):
        return "snow"
    elif weathercode in range(80, 83):
        return "showers"
    elif weathercode >= 95:
        return "storm"
    else:
        return "clear"


def get_wallpaper_key(weather: dict) -> str:
    """
    Given weather dict, return the wallpaper map key to use.
    Priority: special modifiers > base condition
    """
    if not weather:
        return "clear_day"

    weathercode = weather.get("weathercode", 0)
    is_day = weather.get("is_day", 1)
    temperature = weather.get("temperature", 20.0)
    windspeed = weather.get("windspeed", 0.0)

    time_suffix = "day" if is_day == 1 else "night"

    # Advanced modifier rules
    # Wind takes precedence only in clear/partly conditions
    base = get_condition_base(weathercode)

    # Check for modifiers
    if base in ("clear", "partly_cloudy") and windspeed > 25:
        key = f"windy_{time_suffix}"
        logger.info(f"Modifier: windy (windspeed={windspeed} km/h)")
    elif base == "clear" and temperature >= 32:
        key = f"hot_{time_suffix}"
        logger.info(f"Modifier: hot (temp={temperature}°C)")
    elif base == "clear" and temperature <= 15:
        key = f"cold_{time_suffix}"
        logger.info(f"Modifier: cold (temp={temperature}°C)")
    else:
        key = f"{base}_{time_suffix}"

    logger.info(f"Wallpaper key resolved: {key} (code={weathercode}, is_day={is_day})")
    return key


def describe_weather(weather: dict) -> str:
    """Return a human-readable description of current weather."""
    if not weather:
        return "Sem dados de clima"

    weathercode = weather.get("weathercode", 0)
    temperature = weather.get("temperature", 20.0)
    windspeed = weather.get("windspeed", 0.0)
    is_day = weather.get("is_day", 1)

    conditions = {
        0: "Céu limpo",
        1: "Quase limpo",
        2: "Parcialmente nublado",
        3: "Nublado",
        45: "Neblina", 46: "Neblina", 47: "Neblina", 48: "Neblina",
        51: "Garoa leve", 53: "Garoa moderada", 55: "Garoa intensa",
        56: "Garoa gelada", 57: "Garoa gelada intensa",
        61: "Chuva leve", 63: "Chuva moderada", 65: "Chuva intensa",
        66: "Chuva gelada", 67: "Chuva gelada intensa",
        71: "Neve leve", 73: "Neve moderada", 75: "Neve intensa",
        77: "Grãos de neve",
        80: "Pancadas leves", 81: "Pancadas moderadas", 82: "Pancadas intensas",
        85: "Pancadas de neve", 86: "Pancadas de neve intensa",
        95: "Tempestade", 96: "Tempestade com granizo", 99: "Tempestade com granizo forte",
    }

    cond_text = conditions.get(weathercode, f"Código {weathercode}")
    period = "Dia" if is_day == 1 else "Noite"

    return f"{cond_text} • {temperature}°C • Vento {windspeed} km/h • {period}"


def get_condition_emoji(weather: dict) -> str:
    """Return emoji for condition."""
    if not weather:
        return "❓"
    code = weather.get("weathercode", 0)
    is_day = weather.get("is_day", 1)

    if code == 0 or code == 1:
        return "☀️" if is_day else "🌙"
    elif code == 2:
        return "⛅"
    elif code == 3:
        return "☁️"
    elif 45 <= code <= 48:
        return "🌫️"
    elif 51 <= code <= 67:
        return "🌧️"
    elif 71 <= code <= 77:
        return "❄️"
    elif 80 <= code <= 82:
        return "🌦️"
    elif code >= 95:
        return "⛈️"
    return "🌡️"
