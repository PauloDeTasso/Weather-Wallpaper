"""
Wallpaper Controller — Windows 11
SystemParametersInfoW — sem reiniciar Explorer.
Resolve caminhos relativos a assets dentro do .exe via resource_path.
"""

import ctypes
import os
import logging

logger = logging.getLogger(__name__)

SPI_SETDESKWALLPAPER = 0x0014
SPIF_UPDATEINIFILE   = 0x01
SPIF_SENDCHANGE      = 0x02

_last_applied: str | None = None


def _resolve(image_path: str) -> str:
    """
    Se o caminho não for absoluto, tenta localizá-lo:
    1. Relativo ao CWD
    2. Dentro do bundle do .exe (resource_path)
    """
    if os.path.isabs(image_path):
        return image_path

    # Relativo ao CWD (modo dev)
    cwd_path = os.path.abspath(image_path)
    if os.path.isfile(cwd_path):
        return cwd_path

    # Dentro do .exe (modo produção)
    try:
        import builtins
        rp = getattr(builtins, "APP_RESOURCE_PATH", lambda x: x)
        bundled = rp(image_path)
        if os.path.isfile(bundled):
            return bundled
    except Exception:
        pass

    return image_path  # devolve original; set_wallpaper vai reportar erro


def set_wallpaper(image_path: str) -> bool:
    global _last_applied

    if not image_path:
        logger.warning("[Wallpaper] Caminho vazio.")
        return False

    abs_path = _resolve(image_path)

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
        logger.error("[Wallpaper] SystemParametersInfoW retornou 0.")
        return False
    except Exception as e:
        logger.error(f"[Wallpaper] Exceção: {e}")
        return False


def get_current_wallpaper() -> str | None:
    try:
        buf = ctypes.create_unicode_buffer(512)
        ctypes.windll.user32.SystemParametersInfoW(0x0073, len(buf), buf, 0)
        return buf.value or None
    except Exception as e:
        logger.error(f"[Wallpaper] Erro ao obter wallpaper atual: {e}")
        return None
