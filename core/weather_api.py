"""
Weather API - Open-Meteo integration
"""

import requests
import logging
import time

logger = logging.getLogger(__name__)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds


def fetch_weather(latitude: float, longitude: float) -> dict | None:
    """
    Fetch current weather from Open-Meteo API.
    Returns a dict with weather data or None on failure.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": "true",
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"Fetching weather (attempt {attempt}/{MAX_RETRIES}) for lat={latitude}, lon={longitude}")
            response = requests.get(OPEN_METEO_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            weather = data.get("current_weather", {})
            if not weather:
                logger.warning("Empty current_weather in API response.")
                return None

            result = {
                "weathercode": weather.get("weathercode", 0),
                "is_day": weather.get("is_day", 1),
                "temperature": weather.get("temperature", 20.0),
                "windspeed": weather.get("windspeed", 0.0),
                "winddirection": weather.get("winddirection", 0),
                "time": weather.get("time", ""),
            }
            logger.info(f"Weather fetched: {result}")
            return result

        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection error on attempt {attempt}.")
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout on attempt {attempt}.")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching weather: {e}")
            return None

        if attempt < MAX_RETRIES:
            logger.info(f"Retrying in {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)

    logger.error("All retry attempts failed.")
    return None
