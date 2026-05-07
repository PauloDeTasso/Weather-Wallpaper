"""
Wallpaper Controller - Changes Windows 11 desktop wallpaper
"""

import ctypes
import os
import logging

logger = logging.getLogger(__name__)

SPI_SETDESKWALLPAPER = 0x0014
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02

_last_applied_path = None


def set_wallpaper(image_path: str) -> bool:
    """
    Set the Windows 11 desktop wallpaper.
    Returns True on success, False on failure.
    Avoids re-applying the same wallpaper.
    """
    global _last_applied_path

    if not image_path:
        logger.warning("No image path provided.")
        return False

    abs_path = os.path.abspath(image_path)

    if not os.path.exists(abs_path):
        logger.error(f"Image not found: {abs_path}")
        return False

    if abs_path == _last_applied_path:
        logger.info("Wallpaper unchanged, skipping.")
        return True

    ext = os.path.splitext(abs_path)[1].lower()
    if ext not in (".jpg", ".jpeg", ".png", ".bmp"):
        logger.error(f"Unsupported image format: {ext}")
        return False

    try:
        result = ctypes.windll.user32.SystemParametersInfoW(
            SPI_SETDESKWALLPAPER,
            0,
            abs_path,
            SPIF_UPDATEINIFILE | SPIF_SENDCHANGE,
        )
        if result:
            _last_applied_path = abs_path
            logger.info(f"Wallpaper set: {abs_path}")
            return True
        else:
            logger.error("SystemParametersInfoW returned 0 (failure).")
            return False
    except Exception as e:
        logger.error(f"Failed to set wallpaper: {e}")
        return False


def get_current_wallpaper() -> str | None:
    """Get the path of the currently active Windows wallpaper."""
    try:
        buf = ctypes.create_unicode_buffer(512)
        ctypes.windll.user32.SystemParametersInfoW(0x0073, len(buf), buf, 0)
        return buf.value if buf.value else None
    except Exception as e:
        logger.error(f"Failed to get current wallpaper: {e}")
        return None
