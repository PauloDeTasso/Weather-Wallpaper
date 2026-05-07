"""
Configuration Manager - reads/writes config.json
"""

import json
import os
import logging

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "latitude": -7.952,
    "longitude": -37.172,
    "update_interval_minutes": 10,
    "auto_mode": True,
    "start_with_windows": False,
    "image_folder": "assets",
    "wallpaper_map": {
        "clear_day": "assets/clear_day.jpg",
        "clear_night": "assets/clear_night.jpg",
        "partly_cloudy_day": "assets/partly_cloudy_day.jpg",
        "partly_cloudy_night": "assets/partly_cloudy_night.jpg",
        "cloudy_day": "assets/cloudy_day.jpg",
        "cloudy_night": "assets/cloudy_night.jpg",
        "fog_day": "assets/fog_day.jpg",
        "fog_night": "assets/fog_night.jpg",
        "rain_day": "assets/rain_day.jpg",
        "rain_night": "assets/rain_night.jpg",
        "snow_day": "assets/snow_day.jpg",
        "snow_night": "assets/snow_night.jpg",
        "showers_day": "assets/showers_day.jpg",
        "showers_night": "assets/showers_night.jpg",
        "storm_day": "assets/storm_day.jpg",
        "storm_night": "assets/storm_night.jpg",
        "windy_day": "assets/windy_day.jpg",
        "windy_night": "assets/windy_night.jpg",
        "hot_day": "assets/hot_day.jpg",
        "hot_night": "assets/hot_night.jpg",
        "cold_day": "assets/cold_day.jpg",
        "cold_night": "assets/cold_night.jpg",
    },
    "last_weather": None,
    "last_wallpaper": None,
}

CONFIG_PATH = "config.json"


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
                # Merge wallpaper_map
                merged_map = {**DEFAULT_CONFIG["wallpaper_map"], **loaded.get("wallpaper_map", {})}
                self._data["wallpaper_map"] = merged_map
                logger.info("Config loaded from config.json")
            except Exception as e:
                logger.warning(f"Failed to load config: {e}. Using defaults.")
                self._data = dict(DEFAULT_CONFIG)
        else:
            self._data = dict(DEFAULT_CONFIG)
            self.save()

    def save(self):
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value
        self.save()

    def get_wallpaper_map(self):
        return self._data.get("wallpaper_map", {})

    def set_wallpaper_key(self, key, path):
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
