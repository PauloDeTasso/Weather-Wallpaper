"""
Scheduler - Loop de atualização em background
"""

import threading
import time
import logging
from typing import Callable

logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(self, config):
        self.config = config
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._running = False
        self._callbacks: list[Callable] = []

        self.last_weather: dict | None = None
        self.last_weather_data: dict | None = None  # formatted card data
        self.last_key: str | None = None
        self.last_image: str | None = None
        self.last_error: str | None = None
        self.status: str = "Parado"
        self._prev_condition: str | None = None  # para detectar pós-chuva

    def add_callback(self, fn: Callable):
        self._callbacks.append(fn)

    def _notify(self):
        for fn in self._callbacks:
            try:
                fn()
            except Exception as e:
                logger.warning(f"Callback error: {e}")

    def _run_update(self):
        from core.weather_api import fetch_weather
        from core.weather_mapper import get_wallpaper_key, get_weather_card_data, get_condition_key
        from core.wallpaper_controller import set_wallpaper

        lat = self.config.latitude
        lon = self.config.longitude

        self.status = "🔄 Buscando dados do clima..."
        self._notify()

        weather = fetch_weather(lat, lon)

        if weather is None:
            self.last_error = "Falha ao buscar clima. Usando último wallpaper (cache)."
            self.status = "❌ Erro na API — usando cache"
            logger.warning(self.last_error)
            self._notify()
            return

        self.last_weather = weather
        self.last_error = None

        # Detect post_rain: if previous condition was rain/storm and now is clear/partly
        current_cond = get_condition_key(weather)
        if self._prev_condition in ("rain", "storm") and current_cond in ("clear", "partly_cloudy"):
            weather["_override_condition"] = "post_rain"
            logger.info("Post-rain condition detected!")
        self._prev_condition = current_cond

        # Build formatted card data
        card = get_weather_card_data(weather)
        self.last_weather_data = card

        key = get_wallpaper_key(weather)
        # Apply override if set
        if weather.get("_override_condition"):
            from core.weather_mapper import get_period_key
            key = f"{weather['_override_condition']}_{get_period_key(weather)}"

        self.last_key = key

        wallpaper_map = self.config.get_wallpaper_map()
        image_path = wallpaper_map.get(key, "")

        # Fallback chain: try base condition variants
        if not image_path or not __import__("os").path.isfile(image_path):
            fallback_keys = self._fallback_chain(key, wallpaper_map)
            for fb in fallback_keys:
                fp = wallpaper_map.get(fb, "")
                if fp and __import__("os").path.isfile(fp):
                    image_path = fp
                    logger.warning(f"Fallback: '{key}' → '{fb}'")
                    break

        if image_path and __import__("os").path.isfile(image_path):
            self.last_image = image_path
            self.config.set("last_wallpaper", image_path)
            self.config.set("last_weather", weather)
            set_wallpaper(image_path)
            self.status = f"✅ Ativo"
        else:
            self.status = "⚠️ Nenhuma imagem mapeada para esta condição"
            logger.warning(f"No valid image for key: {key}")

        self._notify()

    def _fallback_chain(self, key: str, wallpaper_map: dict) -> list[str]:
        """Gera lista de chaves alternativas para fallback."""
        parts = key.rsplit("_", 1)
        if len(parts) != 2:
            return ["clear_morning"]
        cond, period = parts

        # period fallback order
        period_order = ["morning", "afternoon", "night", "dawn", "dusk", "midnight"]
        chain = []
        for p in period_order:
            if p != period:
                chain.append(f"{cond}_{p}")

        # condition fallback
        cond_fallbacks = {
            "storm": "rain", "post_rain": "clear", "fog": "cloudy",
            "snow": "cloudy", "windy": "clear", "hot": "clear", "cold": "clear"
        }
        if cond in cond_fallbacks:
            fb_cond = cond_fallbacks[cond]
            chain.append(f"{fb_cond}_{period}")
            for p in period_order:
                chain.append(f"{fb_cond}_{p}")

        chain.append("clear_morning")
        return chain

    def _loop(self):
        self._running = True
        logger.info("Scheduler iniciado.")
        while not self._stop_event.is_set():
            try:
                if self.config.auto_mode:
                    self._run_update()
                interval = self.config.update_interval_minutes * 60
                for _ in range(int(interval)):
                    if self._stop_event.is_set():
                        break
                    time.sleep(1)
            except Exception as e:
                logger.error(f"Erro no loop: {e}")
                time.sleep(30)
        self._running = False
        self.status = "⏹ Parado"
        self._notify()

    def start(self):
        if self._running:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True, name="WeatherScheduler")
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        self.status = "⏹ Parando..."
        self._notify()

    def update_now(self):
        t = threading.Thread(target=self._run_update, daemon=True, name="WeatherUpdate")
        t.start()

    @property
    def is_running(self):
        return self._running
