"""
Location Helper - Fetch approximate user location via IP geolocation
"""

import requests
import logging

logger = logging.getLogger(__name__)


def get_location_by_ip() -> tuple[float, float] | None:
    """
    Returns (latitude, longitude) from IP geolocation.
    Uses ip-api.com (free, no key required).
    """
    try:
        response = requests.get("http://ip-api.com/json/", timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get("status") == "success":
            lat = data.get("lat")
            lon = data.get("lon")
            city = data.get("city", "")
            logger.info(f"Location detected: {city} ({lat}, {lon})")
            return float(lat), float(lon)
        else:
            logger.warning("IP geolocation returned non-success status.")
            return None
    except Exception as e:
        logger.error(f"Failed to get location by IP: {e}")
        return None


def validate_coordinates(lat: float, lon: float) -> bool:
    """Validate latitude and longitude ranges."""
    return -90 <= lat <= 90 and -180 <= lon <= 180
