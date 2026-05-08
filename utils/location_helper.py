"""
Location Helper — geolocalização por IP (sem permissão de GPS necessária)
"""

import requests
import logging

logger = logging.getLogger(__name__)


def get_location_by_ip() -> tuple[float, float] | None:
    """
    Retorna (latitude, longitude) via ip-api.com (gratuito, sem chave).
    Retorna None se falhar.
    """
    try:
        resp = requests.get("http://ip-api.com/json/", timeout=6)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") == "success":
            lat  = float(data["lat"])
            lon  = float(data["lon"])
            city = data.get("city", "")
            logger.info(f"[Location] {city}  ({lat}, {lon})")
            return lat, lon
        logger.warning(f"[Location] ip-api status: {data.get('status')}")
    except Exception as e:
        logger.error(f"[Location] Falha: {e}")
    return None


def validate_coordinates(lat: float, lon: float) -> bool:
    return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0
