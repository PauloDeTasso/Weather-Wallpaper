"""
Scheduler - Background thread for periodic weather + wallpaper updates
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
        self._callbacks: list[Callable] = []  # Called after each update

        # Current state
        self.last_weather: dict | None = None
        self.last_key: str | None = None
        self.last_image: str | None = None
        self.last_error: str | None = None
        self.status: str = "Parado"

    def add_callback(self, fn: Callable):
        """Register a callback to be called after each update."""
        self._callbacks.append(fn)

    def _notify(self):
        for fn in self._callbacks:
            try:
                fn()
            except Exception as e:
                logger.warning(f"Callback error: {e}")

    def _run_update(self):
        """Perform a single weather fetch + wallpaper update cycle."""
        from core.weather_api import fetch_weather
        from core.weather_mapper import get_wallpaper_key, describe_weather
        from core.wallpaper_controller import set_wallpaper

        lat = self.config.latitude
        lon = self.config.longitude

        self.status = "Buscando clima..."
        self._notify()

        weather = fetch_weather(lat, lon)

        if weather is None:
            self.last_error = "Falha ao buscar clima. Usando cache."
            self.status = "Erro na API"
            logger.warning(self.last_error)
            # Keep last wallpaper (cache)
            self._notify()
            return

        self.last_weather = weather
        self.last_error = None

        key = get_wallpaper_key(weather)
        self.last_key = key

        wallpaper_map = self.config.get_wallpaper_map()
        image_path = wallpaper_map.get(key)

        if not image_path:
            # Fallback: try without modifier
            base_key = key.rsplit("_", 1)[0] + "_" + key.rsplit("_", 1)[-1]
            image_path = wallpaper_map.get("clear_day")
            logger.warning(f"Key '{key}' not in map, using clear_day fallback.")

        if image_path:
            self.last_image = image_path
            self.config.set("last_wallpaper", image_path)
            self.config.set("last_weather", weather)
            set_wallpaper(image_path)
            self.status = f"Ativo • {describe_weather(weather)}"
        else:
            self.status = "Imagem não configurada"
            logger.warning(f"No image path for key: {key}")

        self._notify()

    def _loop(self):
        """Main scheduler loop."""
        self._running = True
        logger.info("Scheduler started.")
        while not self._stop_event.is_set():
            try:
                if self.config.auto_mode:
                    self._run_update()
                interval = self.config.update_interval_minutes * 60
                # Wait in small chunks so we can stop quickly
                for _ in range(int(interval)):
                    if self._stop_event.is_set():
                        break
                    time.sleep(1)
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
                time.sleep(30)
        self._running = False
        self.status = "Parado"
        self._notify()
        logger.info("Scheduler stopped.")

    def start(self):
        if self._running:
            logger.info("Scheduler already running.")
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True, name="WeatherScheduler")
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        self.status = "Parando..."
        self._notify()

    def update_now(self):
        """Trigger an immediate update in a background thread."""
        t = threading.Thread(target=self._run_update, daemon=True, name="WeatherUpdate")
        t.start()

    @property
    def is_running(self):
        return self._running
