"""
Wallpaper Controller — Windows 11
Usa SystemParametersInfoW para trocar o papel de parede sem reiniciar o Explorer.
"""

import ctypes
import os
import logging

logger = logging.getLogger(__name__)

SPI_SETDESKWALLPAPER = 0x0014
SPIF_UPDATEINIFILE   = 0x01
SPIF_SENDCHANGE      = 0x02

_last_applied: str | None = None


def set_wallpaper(image_path: str) -> bool:
    """
    Define o papel de parede do Windows.
    Ignora se o mesmo arquivo já está ativo (evita piscada desnecessária).
    Retorna True em sucesso, False em falha.
    """
    global _last_applied

    if not image_path:
        logger.warning("[Wallpaper] Caminho vazio, ignorado.")
        return False

    abs_path = os.path.abspath(image_path)

    if not os.path.isfile(abs_path):
        logger.error(f"[Wallpaper] Arquivo não encontrado: {abs_path}")
        return False

    ext = os.path.splitext(abs_path)[1].lower()
    if ext not in (".jpg", ".jpeg", ".png", ".bmp"):
        logger.error(f"[Wallpaper] Formato não suportado: {ext}")
        return False

    if abs_path == _last_applied:
        logger.info("[Wallpaper] Mesmo arquivo — sem alteração.")
        return True

    try:
        ok = ctypes.windll.user32.SystemParametersInfoW(
            SPI_SETDESKWALLPAPER, 0, abs_path,
            SPIF_UPDATEINIFILE | SPIF_SENDCHANGE,
        )
        if ok:
            _last_applied = abs_path
            logger.info(f"[Wallpaper] Aplicado: {abs_path}")
            return True
        else:
            logger.error("[Wallpaper] SystemParametersInfoW retornou 0.")
            return False
    except Exception as e:
        logger.error(f"[Wallpaper] Exceção: {e}")
        return False


def get_current_wallpaper() -> str | None:
    """Retorna o caminho do wallpaper atualmente ativo no Windows."""
    try:
        buf = ctypes.create_unicode_buffer(512)
        ctypes.windll.user32.SystemParametersInfoW(0x0073, len(buf), buf, 0)
        return buf.value or None
    except Exception as e:
        logger.error(f"[Wallpaper] Erro ao obter wallpaper atual: {e}")
        return None
