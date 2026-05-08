"""
Weather Dynamic Wallpaper App
Ponto de entrada principal — Windows 11
"""

import sys
import os
import threading
import logging

# ── Logging ────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.FileHandler("weather_wallpaper.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Iniciando Weather Dynamic Wallpaper App...")

    # Instala dependências se necessário
    try:
        import customtkinter
        import PIL
        import requests
        import pystray
    except ImportError:
        logger.info("Instalando dependências...")
        os.system(f'"{sys.executable}" -m pip install customtkinter pillow requests pystray --quiet')

    # Importações principais
    from utils.config_manager import ConfigManager
    from core.scheduler import Scheduler
    from ui.dashboard import Dashboard
    from ui.tray import TrayApp

    config    = ConfigManager()
    scheduler = Scheduler(config)
    tray      = TrayApp(config, scheduler)

    # Tray em thread daemon
    tray_thread = threading.Thread(target=tray.run, daemon=True, name="TrayThread")
    tray_thread.start()

    # Dashboard (bloqueia até fechar)
    app = Dashboard(config, scheduler, tray)
    app.mainloop()

    logger.info("Aplicativo encerrado.")


if __name__ == "__main__":
    main()
