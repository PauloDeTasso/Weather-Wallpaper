"""
Startup Manager - Add/remove app from Windows startup via registry
"""

import sys
import os
import logging

logger = logging.getLogger(__name__)

APP_NAME = "WeatherWallpaper"


def set_startup(enabled: bool):
    """Add or remove the app from Windows startup registry."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        )
        if enabled:
            exe_path = sys.executable
            script_path = os.path.abspath("main.py")
            value = f'"{exe_path}" "{script_path}"'
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, value)
            logger.info(f"Added to startup: {value}")
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
                logger.info("Removed from startup.")
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except ImportError:
        logger.warning("winreg not available (non-Windows system).")
        return False
    except Exception as e:
        logger.error(f"Failed to modify startup registry: {e}")
        return False


def is_startup_enabled() -> bool:
    """Check if the app is currently in Windows startup."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_READ,
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
