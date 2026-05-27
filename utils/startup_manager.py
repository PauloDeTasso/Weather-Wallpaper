"""
Startup Manager — adiciona/remove o app do início automático do Windows via Registro.

Funciona corretamente em QUALQUER cenário:
  - Rodando como .exe (PyInstaller onefile ou pasta)
  - Rodando como script Python em dev
  - .exe movido para qualquer pasta pelo usuário

sys.executable sempre aponta para o processo em execução no momento
do clique — ou seja, o caminho registrado será sempre o caminho real
e atual do arquivo, onde quer que ele esteja.
"""

import sys
import os
import logging

logger = logging.getLogger(__name__)

APP_NAME = "WeatherWallpaper"


def _get_startup_command() -> str:
    """
    Retorna o comando correto para o registro do Windows.

    - .exe (PyInstaller): sys.frozen = True
      → usa sys.executable diretamente
      → ex: "C:\\Users\\Paulo\\Desktop\\WeatherWallpaper.exe"

    - Script Python (dev): sys.frozen ausente
      → usa python.exe + caminho do main.py
      → ex: "C:\\Python\\python.exe" "C:\\projetos\\main.py"
    """
    if getattr(sys, "frozen", False):
        # Rodando como executável compilado — sys.executable É o .exe
        cmd = f'"{sys.executable}" --minimized'
        logger.info(f"[Startup] Modo .exe detectado: {cmd}")
    else:
        # Rodando como script Python normal (desenvolvimento)
        script = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "main.py")
        )
        cmd = f'"{sys.executable}" "{script}"'
        logger.info(f"[Startup] Modo dev detectado: {cmd}")

    return cmd


def set_startup(enabled: bool) -> bool:
    """
    Ativa ou desativa o início automático com o Windows.
    O caminho registrado é sempre o do executável atual,
    independente de onde o usuário salvou os arquivos.
    """
    try:
        import winreg

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        )

        if enabled:
            cmd = _get_startup_command()
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
            logger.info(f"[Startup] Registrado no Windows: {cmd}")
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
                logger.info("[Startup] Removido do início automático.")
            except FileNotFoundError:
                pass  # Já não existia, sem problema

        winreg.CloseKey(key)
        return True

    except ImportError:
        logger.warning("[Startup] winreg indisponível (não-Windows).")
        return False
    except Exception as e:
        logger.error(f"[Startup] Erro ao modificar registro: {e}")
        return False


def is_startup_enabled() -> bool:
    """Verifica se o app está registrado para iniciar com o Windows."""
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
