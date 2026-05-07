"""
Weather Dynamic Wallpaper App
Main entry point - Windows 11
"""

import sys
import os
import threading
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("weather_wallpaper.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def main():
    logger.info("Starting Weather Dynamic Wallpaper App...")

    try:
        import customtkinter as ctk
    except ImportError:
        logger.error("customtkinter not found. Installing...")
        os.system("pip install customtkinter pillow requests pystray")
        import customtkinter as ctk

    from core.scheduler import Scheduler
    from ui.dashboard import Dashboard
    from ui.tray import TrayApp
    from utils.config_manager import ConfigManager

    config = ConfigManager()
    scheduler = Scheduler(config)

    # Start tray in background thread
    tray = TrayApp(config, scheduler)
    tray_thread = threading.Thread(target=tray.run, daemon=True)
    tray_thread.start()

    # Launch dashboard
    app = Dashboard(config, scheduler, tray)
    app.mainloop()

    logger.info("App closed.")


if __name__ == "__main__":
    main()
