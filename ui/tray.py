"""
Tray App — ícone na bandeja do sistema (Windows 11)
"""

import logging
import threading

logger = logging.getLogger(__name__)


class TrayApp:
    def __init__(self, config, scheduler):
        self.config    = config
        self.scheduler = scheduler
        self._icon     = None
        self._dashboard = None

    def set_dashboard(self, dashboard):
        self._dashboard = dashboard

    # ── Ações do menu ──────────────────────────────────────────────

    def _open(self):
        if self._dashboard:
            try:
                self._dashboard.deiconify()
                self._dashboard.lift()
                self._dashboard.focus_force()
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
        if self._dashboard:
            try:
                self._dashboard.quit()
                self._dashboard.destroy()
            except Exception:
                pass

    # ── Ícone gerado programaticamente ────────────────────────────

    def _make_icon(self):
        from PIL import Image, ImageDraw
        img  = Image.new("RGB", (64, 64), "#0d1117")
        draw = ImageDraw.Draw(img)
        # Sol
        draw.ellipse([14, 14, 50, 50], fill="#fbbf24")
        # Nuvem
        draw.ellipse([8, 32, 36, 56],  fill="#e2e8f0")
        draw.ellipse([20, 26, 52, 54], fill="#e2e8f0")
        draw.ellipse([32, 30, 58, 56], fill="#e2e8f0")
        return img

    # ── Run ────────────────────────────────────────────────────────

    def run(self):
        try:
            import pystray
            from PIL import Image

            icon_img = self._make_icon()

            menu = pystray.Menu(
                pystray.MenuItem("🌤  Abrir Painel",     lambda i, item: self._open()),
                pystray.MenuItem("🔄  Atualizar Agora",  lambda i, item: self._update_now()),
                pystray.MenuItem("⏸  Pausar / Retomar", lambda i, item: self._toggle_pause()),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("✖  Sair",              lambda i, item: self._quit()),
            )

            self._icon = pystray.Icon(
                "WeatherWallpaper",
                icon_img,
                "Weather Wallpaper",
                menu=menu,
            )
            self._icon.run()

        except ImportError:
            logger.warning("[Tray] pystray/PIL não disponível. Tray desabilitado.")
        except Exception as e:
            logger.error(f"[Tray] Erro: {e}")
