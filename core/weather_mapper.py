"""
Weather Mapper
- 6 períodos do dia: dawn, morning, afternoon, dusk, night, midnight
- 11 condições: clear, partly_cloudy, cloudy, rain, storm, post_rain, fog, snow, windy, cold, hot
- Chave final: {condition}_{period}  ex: rain_morning
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ── Períodos do dia ────────────────────────────────────────────────────
PERIODS = [
    ("dawn",      "Amanhecer",  (5,  7)),
    ("morning",   "Manhã",      (7,  12)),
    ("afternoon", "Tarde",      (12, 18)),
    ("dusk",      "Anoitecer",  (18, 20)),
    ("night",     "Noite",      (20, 24)),
    ("midnight",  "Madrugada",  (0,  5)),
]

PERIOD_EMOJIS = {
    "dawn":      "🌅",
    "morning":   "🌄",
    "afternoon": "☀️",
    "dusk":      "🌇",
    "night":     "🌃",
    "midnight":  "🌌",
}

# ── Condições ──────────────────────────────────────────────────────────
CONDITIONS = [
    ("clear",         "Céu Limpo"),
    ("partly_cloudy", "Parcialmente Nublado"),
    ("cloudy",        "Nublado"),
    ("rain",          "Chuva"),
    ("storm",         "Tempestade"),
    ("post_rain",     "Pós-Chuva"),
    ("fog",           "Neblina"),
    ("snow",          "Neve"),
    ("windy",         "Vento Forte"),
    ("cold",          "Frio"),
    ("hot",           "Calor Extremo"),
]

CONDITION_EMOJIS = {
    "clear":         "☀️",
    "partly_cloudy": "⛅",
    "cloudy":        "☁️",
    "rain":          "🌧️",
    "storm":         "⛈️",
    "post_rain":     "🌈",
    "fog":           "🌫️",
    "snow":          "❄️",
    "windy":         "💨",
    "cold":          "🧊",
    "hot":           "🔥",
}

# ── WMO weathercode → condição base ───────────────────────────────────
WEATHERCODE_MAP = {
    0:  "clear",
    1:  "clear",
    2:  "partly_cloudy",
    3:  "cloudy",
    45: "fog", 46: "fog", 47: "fog", 48: "fog",
    51: "rain", 53: "rain", 55: "rain",
    56: "rain", 57: "rain",
    61: "rain", 63: "rain", 65: "rain",
    66: "rain", 67: "rain",
    71: "snow", 73: "snow", 75: "snow", 77: "snow",
    80: "rain", 81: "rain", 82: "rain",
    85: "snow", 86: "snow",
    95: "storm", 96: "storm", 99: "storm",
}

# Descrições WMO completas em PT-BR
WEATHERCODE_LABELS = {
    0:  "Céu completamente limpo",
    1:  "Predominantemente limpo",
    2:  "Parcialmente nublado",
    3:  "Nublado / Encoberto",
    45: "Neblina",
    46: "Neblina depositante",
    47: "Neblina espessa",
    48: "Neblina com geada",
    51: "Garoa fraca",
    53: "Garoa moderada",
    55: "Garoa densa",
    56: "Garoa fraca congelante",
    57: "Garoa densa congelante",
    61: "Chuva leve",
    63: "Chuva moderada",
    65: "Chuva forte",
    66: "Chuva fraca congelante",
    67: "Chuva forte congelante",
    71: "Neve leve",
    73: "Neve moderada",
    75: "Neve forte",
    77: "Grãos de neve",
    80: "Pancadas de chuva leves",
    81: "Pancadas de chuva moderadas",
    82: "Pancadas de chuva violentas",
    85: "Pancadas de neve leves",
    86: "Pancadas de neve fortes",
    95: "Trovoada",
    96: "Trovoada com granizo leve",
    99: "Trovoada com granizo forte",
}


def get_period_from_hour(hour: int) -> str:
    """Retorna a chave do período baseado na hora local."""
    for key, _, (start, end) in PERIODS:
        if start <= hour < end:
            return key
    return "night"


def get_period_key(weather: dict) -> str:
    """
    Determina o período do dia.
    Usa a hora local do sistema (mais preciso que is_day).
    """
    now_hour = datetime.now().hour
    period = get_period_from_hour(now_hour)
    logger.debug(f"Period resolved: {period} (hour={now_hour})")
    return period


def get_condition_key(weather: dict) -> str:
    """Determina a condição climática com modificadores."""
    code = weather.get("weathercode", 0)
    temp = weather.get("temperature", 20.0)
    wind = weather.get("windspeed", 0.0)

    base = WEATHERCODE_MAP.get(code, "clear")

    # Modificadores de temperatura e vento (só aplicados em condições neutras)
    if base == "clear":
        if wind > 25:
            return "windy"
        if temp >= 35:
            return "hot"
        if temp <= 10:
            return "cold"

    if base == "partly_cloudy":
        if wind > 25:
            return "windy"
        if temp <= 10:
            return "cold"

    return base


def get_wallpaper_key(weather: dict) -> str:
    """Retorna a chave completa: {condition}_{period}"""
    condition = get_condition_key(weather)
    period = get_period_key(weather)
    key = f"{condition}_{period}"
    logger.info(f"Wallpaper key: {key}")
    return key


def get_period_label(period_key: str) -> str:
    for k, label, _ in PERIODS:
        if k == period_key:
            return label
    return period_key


def get_condition_label(condition_key: str) -> str:
    for k, label in CONDITIONS:
        if k == condition_key:
            return label
    return condition_key


def get_full_label(wallpaper_key: str) -> str:
    """Ex: 'rain_morning' → 'Chuva — Manhã'"""
    parts = wallpaper_key.rsplit("_", 1)
    if len(parts) == 2:
        cond, period = parts
        # handle conditions with underscore like partly_cloudy
        # actually key format: {condition}_{period}, period is last token
        return f"{get_condition_label(cond)} — {get_period_label(period)}"
    return wallpaper_key


def get_weather_card_data(weather: dict) -> dict:
    """
    Retorna dict com todos os dados formatados para exibição no painel.
    """
    if not weather:
        return {}

    code = weather.get("weathercode", 0)
    temp = weather.get("temperature", 20.0)
    wind = weather.get("windspeed", 0.0)
    winddir = weather.get("winddirection", 0)
    is_day = weather.get("is_day", 1)
    time_str = weather.get("time", "")

    condition_key = get_condition_key(weather)
    period_key = get_period_key(weather)

    # Direção do vento em texto
    def wind_direction_text(deg):
        dirs = ["Norte", "Nordeste", "Leste", "Sudeste",
                "Sul", "Sudoeste", "Oeste", "Noroeste"]
        idx = round(deg / 45) % 8
        return dirs[idx]

    # Sensação térmica simplificada (índice de calor / wind chill)
    feels = temp
    if temp > 27 and wind < 5:
        feels = temp + 2
    elif wind > 20:
        feels = temp - round(wind * 0.1, 1)

    # Intensidade do vento
    def wind_label(kmh):
        if kmh < 5:   return "Calmo"
        if kmh < 20:  return "Fraco"
        if kmh < 40:  return "Moderado"
        if kmh < 60:  return "Forte"
        if kmh < 90:  return "Muito forte"
        return "Tempestuoso"

    return {
        "condition_key":   condition_key,
        "condition_label": get_condition_label(condition_key),
        "condition_emoji": CONDITION_EMOJIS.get(condition_key, "🌡️"),
        "period_key":      period_key,
        "period_label":    get_period_label(period_key),
        "period_emoji":    PERIOD_EMOJIS.get(period_key, "🕐"),
        "weathercode":     code,
        "weathercode_label": WEATHERCODE_LABELS.get(code, f"Código {code}"),
        "temperature":     temp,
        "feels_like":      round(feels, 1),
        "windspeed":       wind,
        "wind_label":      wind_label(wind),
        "winddirection":   winddir,
        "wind_dir_text":   wind_direction_text(winddir),
        "is_day":          is_day,
        "period_of_day":   "Dia" if is_day else "Noite",
        "api_time":        time_str,
        "wallpaper_key":   f"{condition_key}_{period_key}",
    }
