"""
Configuration Manager - config.json
Suporta 66 combinações: 11 condições × 6 períodos
"""

import json
import os
import logging

logger = logging.getLogger(__name__)
CONFIG_PATH = "config.json"

# 11 condições × 6 períodos = 66 chaves
CONDITIONS = [
    "clear", "partly_cloudy", "cloudy", "rain",
    "storm", "post_rain", "fog", "snow", "windy", "cold", "hot"
]
PERIODS = ["dawn", "morning", "afternoon", "dusk", "night", "midnight"]


def _build_default_map() -> dict:
    m = {}
    for cond in CONDITIONS:
        for period in PERIODS:
            key = f"{cond}_{period}"
            m[key] = f"assets/{key}.jpg"
    return m


DEFAULT_CONFIG = {
    "latitude": -7.952,
    "longitude": -37.172,
    "update_interval_minutes": 10,
    "auto_mode": True,
    "start_with_windows": False,
    "wallpaper_map": _build_default_map(),
    "last_weather": None,
    "last_wallpaper": None,
}


class ConfigManager:
    def __init__(self):
        self._data = {}
        self.load()

    def load(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                self._data = {**DEFAULT_CONFIG, **loaded}
                merged = {**_build_default_map(), **loaded.get("wallpaper_map", {})}
                self._data["wallpaper_map"] = merged
                logger.info("Config carregado.")
            except Exception as e:
                logger.warning(f"Erro ao carregar config: {e}. Usando padrão.")
                self._data = dict(DEFAULT_CONFIG)
                self._data["wallpaper_map"] = _build_default_map()
        else:
            self._data = dict(DEFAULT_CONFIG)
            self._data["wallpaper_map"] = _build_default_map()
            self.save()

    def save(self):
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar config: {e}")

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value
        self.save()

    def get_wallpaper_map(self) -> dict:
        return self._data.get("wallpaper_map", {})

    def set_wallpaper_key(self, key: str, path: str):
        self._data["wallpaper_map"][key] = path
        self.save()

    @property
    def latitude(self):
        return self._data.get("latitude", -7.952)

    @latitude.setter
    def latitude(self, v):
        self._data["latitude"] = v
        self.save()

    @property
    def longitude(self):
        return self._data.get("longitude", -37.172)

    @longitude.setter
    def longitude(self, v):
        self._data["longitude"] = v
        self.save()

    @property
    def update_interval_minutes(self):
        return self._data.get("update_interval_minutes", 10)

    @update_interval_minutes.setter
    def update_interval_minutes(self, v):
        self._data["update_interval_minutes"] = v
        self.save()

    @property
    def auto_mode(self):
        return self._data.get("auto_mode", True)

    @auto_mode.setter
    def auto_mode(self, v):
        self._data["auto_mode"] = v
        self.save()

    @property
    def start_with_windows(self):
        return self._data.get("start_with_windows", False)

    @start_with_windows.setter
    def start_with_windows(self, v):
        self._data["start_with_windows"] = v
        self.save()
