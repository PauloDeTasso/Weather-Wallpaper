"""
Configuration Manager — config.json
Compatível com PyInstaller (--onefile):
  - Lê o config padrão de dentro do .exe (resource_path)
  - Salva alterações do usuário em %APPDATA%\WeatherWallpaper\config.json
"""

import json
import os
import shutil
import logging

logger = logging.getLogger(__name__)

CONDITIONS = [
    "clear", "partly_cloudy", "cloudy", "rain",
    "storm", "post_rain", "fog", "snow", "windy", "cold", "hot"
]
PERIODS = ["dawn", "morning", "afternoon", "dusk", "night", "midnight"]


def _build_default_map() -> dict:
    return {f"{c}_{p}": f"assets/{c}_{p}.jpg"
            for c in CONDITIONS for p in PERIODS}


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


def _user_config_path() -> str:
    """Caminho gravável em %APPDATA%\WeatherWallpaper\config.json"""
    import builtins
    base = getattr(builtins, "APP_USER_DATA_DIR",
                   os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "config.json")


def _bundled_config_path() -> str:
    """config.json empacotado dentro do .exe (somente leitura)"""
    import builtins
    rp = getattr(builtins, "APP_RESOURCE_PATH", lambda x: x)
    return rp("config.json")


class ConfigManager:
    def __init__(self):
        self._data = {}
        self._save_path = _user_config_path()
        self.load()

    def load(self):
        # 1. Tenta carregar do %APPDATA% (config do usuário)
        if os.path.exists(self._save_path):
            try:
                with open(self._save_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                self._data = {**DEFAULT_CONFIG, **loaded}
                self._data["wallpaper_map"] = {
                    **_build_default_map(),
                    **loaded.get("wallpaper_map", {})
                }
                logger.info(f"Config carregado de {self._save_path}")
                return
            except Exception as e:
                logger.warning(f"Erro ao ler config do usuário: {e}")

        # 2. Tenta carregar o config padrão empacotado no .exe
        bundled = _bundled_config_path()
        if os.path.exists(bundled):
            try:
                with open(bundled, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                self._data = {**DEFAULT_CONFIG, **loaded}
                self._data["wallpaper_map"] = {
                    **_build_default_map(),
                    **loaded.get("wallpaper_map", {})
                }
                logger.info(f"Config padrão carregado de {bundled}")
                self.save()  # copia para %APPDATA% para edições futuras
                return
            except Exception as e:
                logger.warning(f"Erro ao ler config empacotado: {e}")

        # 3. Fallback total: usa defaults hardcoded
        self._data = dict(DEFAULT_CONFIG)
        self._data["wallpaper_map"] = _build_default_map()
        logger.info("Usando configuração padrão hardcoded.")
        self.save()

    def save(self):
        try:
            os.makedirs(os.path.dirname(self._save_path), exist_ok=True)
            with open(self._save_path, "w", encoding="utf-8") as f:
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
        self._data["latitude"] = v; self.save()

    @property
    def longitude(self):
        return self._data.get("longitude", -37.172)

    @longitude.setter
    def longitude(self, v):
        self._data["longitude"] = v; self.save()

    @property
    def update_interval_minutes(self):
        return self._data.get("update_interval_minutes", 10)

    @update_interval_minutes.setter
    def update_interval_minutes(self, v):
        self._data["update_interval_minutes"] = v; self.save()

    @property
    def auto_mode(self):
        return self._data.get("auto_mode", True)

    @auto_mode.setter
    def auto_mode(self, v):
        self._data["auto_mode"] = v; self.save()

    @property
    def start_with_windows(self):
        return self._data.get("start_with_windows", False)

    @start_with_windows.setter
    def start_with_windows(self, v):
        self._data["start_with_windows"] = v; self.save()
