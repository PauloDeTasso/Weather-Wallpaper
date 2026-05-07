"""
Tray App - System tray icon for Windows 11
"""

import logging
import threading

logger = logging.getLogger(__name__)


class TrayApp:
    def __init__(self, config, scheduler):
        self.config = config
        self.scheduler = scheduler
        self._icon = None
        self._dashboard_ref = None

    def set_dashboard(self, dashboard):
        self._dashboard_ref = dashboard

    def _open_dashboard(self):
        if self._dashboard_ref:
            try:
                self._dashboard_ref.deiconify()
                self._dashboard_ref.lift()
                self._dashboard_ref.focus_force()
            except Exception:
                pass

    def _update_now(self):
        self.scheduler.update_now()

    def _toggle_pause(self):
        if self.scheduler.is_running:
            self.scheduler.stop()
        else:
            self.scheduler.start()

    def _quit(self):
        self.scheduler.stop()
        if self._icon:
            self._icon.stop()
        if self._dashboard_ref:
            try:
                self._dashboard_ref.quit()
                self._dashboard_ref.destroy()
            except Exception:
                pass

    def run(self):
        try:
            import pystray
            from PIL import Image, ImageDraw

            # Create a simple icon
            img = Image.new("RGB", (64, 64), color=(30, 120, 200))
            draw = ImageDraw.Draw(img)
            draw.ellipse([8, 8, 56, 56], fill=(255, 200, 50))
            draw.ellipse([16, 28, 48, 60], fill=(255, 255, 255))

            menu = pystray.Menu(
                pystray.MenuItem("Abrir Painel", lambda icon, item: self._open_dashboard()),
                pystray.MenuItem("Atualizar Agora", lambda icon, item: self._update_now()),
                pystray.MenuItem("Pausar/Retomar", lambda icon, item: self._toggle_pause()),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Sair", lambda icon, item: self._quit()),
            )

            self._icon = pystray.Icon(
                "WeatherWallpaper",
                img,
                "Weather Wallpaper",
                menu=menu,
            )
            self._icon.run()
        except ImportError:
            logger.warning("pystray/PIL not available. Tray disabled.")
        except Exception as e:
            logger.error(f"Tray error: {e}")
