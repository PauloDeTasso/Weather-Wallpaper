"""
Location Helper — geolocalização por IP (sem permissão de GPS necessária)

Estratégia:
  1. Tenta 3 provedores gratuitos em sequência (ip-api → ipapi.co → ipinfo.io).
  2. Faz "snap" para a cidade conhecida mais próxima (haversine, raio 300 km).
     Isso corrige o erro típico de GeoIP no interior (ex: IP de Iguatu-CE
     quando o usuário está em Imaculada-PB / Santa Terezinha-PE, ~225 km).
"""

import math
import requests
import logging

logger = logging.getLogger(__name__)

# ── Cidades conhecidas do usuário (coordenadas oficiais Open-Meteo) ────
KNOWN_LOCATIONS: list[dict] = [
    {"name": "Imaculada-PB",       "latitude": -7.38972, "longitude": -37.50917},
    {"name": "Santa Terezinha-PE", "latitude": -7.37778, "longitude": -37.48},
]

SNAP_RADIUS_KM = 300.0


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distância em km entre dois pontos (fórmula de Haversine)."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def snap_to_known_location(
    lat: float, lon: float, max_km: float = SNAP_RADIUS_KM
) -> tuple[float, float, str, float] | None:
    """
    Retorna (latitude, longitude, nome, distância_km) da cidade conhecida
    mais próxima, ou None se todas estiverem além de max_km.
    """
    best = None
    best_dist = float("inf")
    for loc in KNOWN_LOCATIONS:
        d = haversine_km(lat, lon, loc["latitude"], loc["longitude"])
        if d < best_dist:
            best_dist = d
            best = loc
    if best is not None and best_dist <= max_km:
        return best["latitude"], best["longitude"], best["name"], best_dist
    return None


def _try_providers() -> tuple[float, float, str, str] | None:
    """Tenta provedores em sequência. Retorna (lat, lon, cidade_raw, provedor)."""
    # 1. ip-api.com (sem chave)
    try:
        resp = requests.get("http://ip-api.com/json/", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") == "success":
            return (float(data["lat"]), float(data["lon"]),
                    str(data.get("city", "")), "ip-api")
    except Exception as e:
        logger.warning(f"[Location] ip-api falhou: {e}")

    # 2. ipapi.co (sem chave, limite generoso)
    try:
        resp = requests.get("https://ipapi.co/json/", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if "latitude" in data and "longitude" in data and data.get("latitude"):
            return (float(data["latitude"]), float(data["longitude"]),
                    str(data.get("city", "")), "ipapi.co")
    except Exception as e:
        logger.warning(f"[Location] ipapi.co falhou: {e}")

    # 3. ipinfo.io (sem token, cota básica)
    try:
        resp = requests.get("https://ipinfo.io/json", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        loc = data.get("loc", "")
        if "," in loc:
            la, lo = loc.split(",", 1)
            return (float(la), float(lo),
                    str(data.get("city", "")), "ipinfo.io")
    except Exception as e:
        logger.warning(f"[Location] ipinfo.io falhou: {e}")

    return None


def get_location_detail() -> dict | None:
    """
    Detecção completa com snap. Retorna:
      {latitude, longitude, raw_lat, raw_lon, raw_city, provider,
       snapped, city, distance_km}
    ou None se todos os provedores falharem.
    """
    raw = _try_providers()
    if not raw:
        logger.error("[Location] Todos os provedores falharam.")
        return None
    lat, lon, city_raw, provider = raw
    snapped = snap_to_known_location(lat, lon)
    if snapped:
        slat, slon, name, dist = snapped
        logger.info(f"[Location] IP ({provider})={city_raw} ({lat}, {lon}) → "
                    f"snap {name} ({slat}, {slon}) a {dist:.1f} km")
        return {
            "latitude": slat, "longitude": slon,
            "raw_lat": lat, "raw_lon": lon, "raw_city": city_raw,
            "provider": provider, "snapped": True,
            "city": name, "distance_km": round(dist, 1),
        }
    logger.info(f"[Location] {city_raw} ({lat}, {lon}) via {provider} (sem snap)")
    return {
        "latitude": lat, "longitude": lon,
        "raw_lat": lat, "raw_lon": lon, "raw_city": city_raw,
        "provider": provider, "snapped": False,
        "city": city_raw, "distance_km": 0.0,
    }


def get_location_by_ip() -> tuple[float, float] | None:
    """
    Retorna (latitude, longitude) com snap para cidade conhecida.
    Mantém assinatura antiga para compatibilidade.
    Retorna None se falhar.
    """
    detail = get_location_detail()
    if not detail:
        return None
    return detail["latitude"], detail["longitude"]


def validate_coordinates(lat: float, lon: float) -> bool:
    return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0
