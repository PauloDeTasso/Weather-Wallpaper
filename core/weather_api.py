"""
Weather API — Open-Meteo
Sem API key. Gratuito. Retry automático.
"""

import requests
import logging
import time

logger = logging.getLogger(__name__)

BASE_URL     = "https://api.open-meteo.com/v1/forecast"
MAX_RETRIES  = 3
RETRY_DELAY  = 5  # segundos


def fetch_weather(latitude: float, longitude: float) -> dict | None:
    """
    Consulta a API Open-Meteo e retorna os dados de clima atual.
    Retorna None em caso de falha total (todos os retries esgotados).
    """
    params = {
        "latitude":        latitude,
        "longitude":       longitude,
        "current_weather": "true",
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info(f"[API] Tentativa {attempt}/{MAX_RETRIES}  lat={latitude}  lon={longitude}")
            resp = requests.get(BASE_URL, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            cw = data.get("current_weather", {})
            if not cw:
                logger.warning("[API] Resposta sem 'current_weather'.")
                return None

            result = {
                "weathercode":  int(cw.get("weathercode", 0)),
                "is_day":       int(cw.get("is_day", 1)),
                "temperature":  float(cw.get("temperature", 20.0)),
                "windspeed":    float(cw.get("windspeed", 0.0)),
                "winddirection":float(cw.get("winddirection", 0)),
                "time":         cw.get("time", ""),
            }
            logger.info(f"[API] OK → {result}")
            return result

        except requests.exceptions.ConnectionError:
            logger.warning(f"[API] Erro de conexão (tentativa {attempt}).")
        except requests.exceptions.Timeout:
            logger.warning(f"[API] Timeout (tentativa {attempt}).")
        except requests.exceptions.HTTPError as e:
            logger.error(f"[API] HTTP error: {e}")
            return None
        except Exception as e:
            logger.error(f"[API] Erro inesperado: {e}")
            return None

        if attempt < MAX_RETRIES:
            logger.info(f"[API] Aguardando {RETRY_DELAY}s antes de nova tentativa...")
            time.sleep(RETRY_DELAY)

    logger.error("[API] Todas as tentativas falharam.")
    return None
