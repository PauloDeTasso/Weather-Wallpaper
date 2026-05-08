"""
Weather Dynamic Wallpaper App
Ponto de entrada principal — Windows 11

Compatível com PyInstaller (--onefile --windowed).
"""

import sys
import os
import threading
import logging


# ── Resolver caminhos de recursos empacotados no .exe ──────────────
def resource_path(relative: str) -> str:
    """
    Retorna caminho absoluto de um recurso lido (assets, config padrão).
    Dentro do .exe  → sys._MEIPASS  (pasta temporária do PyInstaller)
    Em dev          → diretório do próprio script
    """
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)


# ── Diretório gravável pelo usuário (%APPDATA%\WeatherWallpaper) ────
def user_data_dir() -> str:
    """
    Pasta onde o app GRAVA arquivos (config.json editado, log).
    Fica fora do .exe — em %APPDATA%\\WeatherWallpaper no Windows.
    """
    appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
    path = os.path.join(appdata, "WeatherWallpaper")
    os.makedirs(path, exist_ok=True)
    return path


# Expõe para todos os módulos via builtins (importado antes dos demais)
import builtins
builtins.APP_RESOURCE_PATH = resource_path
builtins.APP_USER_DATA_DIR = user_data_dir()


# ── Logging ────────────────────────────────────────────────────────
LOG_FILE = os.path.join(user_data_dir(), "weather_wallpaper.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        # Sem StreamHandler: --windowed não tem console
    ],
)
logger = logging.getLogger(__name__)


def main():
    logger.info("=== Weather Dynamic Wallpaper App iniciado ===")
    logger.info(f"user_data_dir  = {user_data_dir()}")
    logger.info(f"resource_base  = {resource_path('.')}")

    from utils.config_manager import ConfigManager
    from core.scheduler import Scheduler
    from ui.dashboard import Dashboard
    from ui.tray import TrayApp

    config    = ConfigManager()
    scheduler = Scheduler(config)
    tray      = TrayApp(config, scheduler)

    tray_thread = threading.Thread(target=tray.run, daemon=True, name="TrayThread")
    tray_thread.start()

    app = Dashboard(config, scheduler, tray)
    app.mainloop()

    logger.info("Aplicativo encerrado.")


if __name__ == "__main__":
    main()
