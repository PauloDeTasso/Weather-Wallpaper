"""
Startup Manager — adiciona/remove o app do início automático do Windows via Registro
"""

import sys
import os
import logging

logger = logging.getLogger(__name__)

APP_NAME = "WeatherWallpaper"


def set_startup(enabled: bool) -> bool:
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_SET_VALUE,
        )
        if enabled:
            exe  = sys.executable
            script = os.path.abspath("main.py")
            value  = f'"{exe}" "{script}"'
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, value)
            logger.info(f"[Startup] Adicionado: {value}")
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
                logger.info("[Startup] Removido do início automático.")
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except ImportError:
        logger.warning("[Startup] winreg indisponível (não-Windows).")
        return False
    except Exception as e:
        logger.error(f"[Startup] Erro: {e}")
        return False


def is_startup_enabled() -> bool:
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0, winreg.KEY_READ,
        )
        try:
            winreg.QueryValueEx(key, APP_NAME)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            winreg.CloseKey(key)
            return False
    except Exception:
        return False
