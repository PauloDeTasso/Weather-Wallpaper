"""
Configuration Manager — config.json
Compatível com PyInstaller (--onefile):
  - Lê o config padrão de dentro do .exe (resource_path)
  - Salva alterações do usuário em APPDATA/WeatherWallpaper/config.json
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
    # Novo padrão canônico: images/<condition>/<period>.jpg
    # (o sync corrige a extensão real .png/.jpg na primeira carga)
    return {f"{c}_{p}": os.path.join("images", c, f"{p}.jpg")
            for c in CONDITIONS for p in PERIODS}


DEFAULT_CONFIG = {
    "latitude": -7.952,
    "longitude": -37.172,
    "auto_detect_location": True,
    "update_interval_minutes": 10,
    "auto_mode": True,
    "start_with_windows": False,
    "wallpaper_map": _build_default_map(),
    "last_weather": None,
    "last_wallpaper": None,
}


def _user_config_path() -> str:
    """Caminho gravável em APPDATA/WeatherWallpaper/config.json"""
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
        # Auto-scan: assume fotos novas copiadas p/ images/<cond>/<periodo>
        try:
            rep = self.sync_auto_images()
            logger.info(f"[Config] imagens: {rep['auto']} auto + {rep['manual']} manual, "
                        f"{rep['missing']} faltantes de {rep['total']}.")
        except Exception as e:
            logger.warning(f"[Config] sync_auto_images falhou: {e}")

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

    def sync_auto_images(self) -> dict:
        """
        Preenche o wallpaper_map com as fotos encontradas por convenção
        images/<condition>/<period>.<ext> — SEM sobrescrever overrides manuais.

        Regra por slot:
          - se o valor atual está vazio / arquivo não existe / é default antigo
            'assets/...' inexistente → assume o auto (se houver)
          - se o valor atual existe e é diferente do auto → mantém (manual)
        Retorna o coverage_report do image_store.
        """
        try:
            from utils.image_store import scan_all
        except ImportError:
            from image_store import scan_all  # fallback

        wallpaper_map = self._data.get("wallpaper_map", {})
        scanned = scan_all(wallpaper_map)

        changed = 0
        for key, info in scanned.items():
            if info["source"] == "auto" and info["path"]:
                current = (wallpaper_map.get(key) or "").strip()
                # normaliza p/ comparação
                try:
                    same = os.path.abspath(current) == os.path.abspath(info["path"])
                except Exception:
                    same = current == info["path"]
                if not same:
                    # só sobrescreve se atual for vazio / inexistente / default
                    # legado / temp obsoleta de bundle antigo (_MEI...)
                    upper = current.upper()
                    if (not current
                            or "_MEI" in upper
                            or not os.path.isfile(current)
                            or current.replace("\\", "/").startswith("assets/")):
                        wallpaper_map[key] = info["path"]
                        changed += 1
        self._data["wallpaper_map"] = wallpaper_map
        if changed:
            self.save()
            logger.info(f"[Config] sync_auto_images: {changed} slots atualizados do disco.")
        try:
            from utils.image_store import coverage_report
        except ImportError:
            from image_store import coverage_report
        return coverage_report(wallpaper_map)

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

    @property
    def auto_detect_location(self):
        return self._data.get("auto_detect_location", True)

    @auto_detect_location.setter
    def auto_detect_location(self, v):
        self._data["auto_detect_location"] = bool(v); self.save()

    def maybe_auto_detect_location(self, force: bool = False) -> bool:
        """
        Detecta (lat, lon) via IP e persiste em %APPDATA%/config.json.

        - Só executa se auto_detect_location=True (ou force=True).
        - Retorna True se as coordenadas foram atualizadas e salvas.
        - Nunca apaga coordenadas válidas em caso de falha de rede.
        """
        if not force and not self._data.get("auto_detect_location", True):
            logger.info("[Config] auto-detect de localização desativado — mantendo "
                        f"({self.latitude}, {self.longitude}).")
            return False
        try:
            try:
                from utils.location_helper import get_location_detail
            except ImportError:
                from location_helper import get_location_detail  # fallback
            detail = get_location_detail()
        except Exception as e:
            logger.warning(f"[Config] auto-detect falhou: {e}")
            return False
        if not detail:
            logger.warning("[Config] auto-detect sem resposta — mantendo coordenadas atuais.")
            return False
        lat, lon = detail["latitude"], detail["longitude"]
        city = detail.get("city", "")
        dist = detail.get("distance_km", 0.0)
        # Evita regravação desnecessária (tolerância ~100m)
        try:
            if (abs(float(lat) - float(self.latitude)) < 0.001
                    and abs(float(lon) - float(self.longitude)) < 0.001):
                logger.info(f"[Config] localização inalterada ({lat}, {lon}) — nada a salvar.")
                return False
        except Exception:
            pass
        self._data["latitude"] = float(lat)
        self._data["longitude"] = float(lon)
        self.save()
        tag = f" ({city} a {dist} km do IP)" if detail.get("snapped") else (f" ({city})" if city else "")
        logger.info(f"[Config] localização auto-detectada e persistida: ({lat}, {lon}){tag}")
        return True
