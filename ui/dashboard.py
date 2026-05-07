"""
Dashboard - Modern Windows 11 UI using CustomTkinter
"""

import os
import threading
import logging
import tkinter as tk
from tkinter import filedialog, messagebox

logger = logging.getLogger(__name__)

try:
    import customtkinter as ctk
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
except ImportError:
    ctk = None

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# All 21 wallpaper condition keys with friendly labels
CONDITION_KEYS = [
    ("clear_day", "☀️ Céu limpo - Dia"),
    ("clear_night", "🌙 Céu limpo - Noite"),
    ("partly_cloudy_day", "⛅ Parcialmente nublado - Dia"),
    ("partly_cloudy_night", "🌃 Parcialmente nublado - Noite"),
    ("cloudy_day", "☁️ Nublado - Dia"),
    ("cloudy_night", "☁️ Nublado - Noite"),
    ("fog_day", "🌫️ Neblina - Dia"),
    ("fog_night", "🌫️ Neblina - Noite"),
    ("rain_day", "🌧️ Chuva - Dia"),
    ("rain_night", "🌧️ Chuva - Noite"),
    ("snow_day", "❄️ Neve - Dia"),
    ("snow_night", "❄️ Neve - Noite"),
    ("showers_day", "🌦️ Pancadas - Dia"),
    ("showers_night", "🌦️ Pancadas - Noite"),
    ("storm_day", "⛈️ Tempestade - Dia"),
    ("storm_night", "⛈️ Tempestade - Noite"),
    ("windy_day", "💨 Vento forte - Dia"),
    ("windy_night", "💨 Vento forte - Noite"),
    ("hot_day", "🔥 Calor extremo - Dia"),
    ("hot_night", "🔥 Calor extremo - Noite"),
    ("cold_day", "🧊 Frio - Dia"),
    ("cold_night", "🧊 Frio - Noite"),
]


class Dashboard(ctk.CTk if ctk else tk.Tk):
    def __init__(self, config, scheduler, tray=None):
        super().__init__()

        self.config_mgr = config
        self.scheduler = scheduler
        self.tray = tray

        if tray:
            tray.set_dashboard(self)

        # Register scheduler callback
        self.scheduler.add_callback(self._on_scheduler_update)

        self._setup_window()
        self._build_ui()
        self._load_values()

        # Start scheduler
        self.scheduler.start()

        # Handle close → minimize to tray
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _setup_window(self):
        self.title("Weather Wallpaper • Windows 11")
        self.geometry("900x700")
        self.minsize(800, 600)
        if ctk:
            self.configure(fg_color="#0f0f0f")

    def _build_ui(self):
        # ── Top bar ──────────────────────────────────────────────
        top = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=0, height=60)
        top.pack(fill="x", side="top")
        top.pack_propagate(False)

        ctk.CTkLabel(
            top,
            text="🌤  Weather Wallpaper",
            font=("Segoe UI", 22, "bold"),
            text_color="#e2e8f0",
        ).pack(side="left", padx=24, pady=10)

        self._status_label = ctk.CTkLabel(
            top,
            text="● Iniciando...",
            font=("Segoe UI", 12),
            text_color="#64748b",
        )
        self._status_label.pack(side="right", padx=24)

        # ── Main layout ──────────────────────────────────────────
        main = ctk.CTkFrame(self, fg_color="#0f0f0f")
        main.pack(fill="both", expand=True, padx=0, pady=0)
        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=1)
        main.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(main, fg_color="#0f0f0f")
        left.grid(row=0, column=0, sticky="nsew", padx=(16, 8), pady=16)

        right = ctk.CTkScrollableFrame(main, fg_color="#111827", corner_radius=12)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 16), pady=16)

        self._build_left(left)
        self._build_right(right)

    def _build_left(self, parent):
        """Left panel: location, settings, controls, preview"""

        # ── Location card ────────────────────────────────────────
        loc_card = self._card(parent, "📍 Localização")

        self._lat_var = ctk.StringVar()
        self._lon_var = ctk.StringVar()

        ctk.CTkLabel(loc_card, text="Latitude", font=("Segoe UI", 12), text_color="#94a3b8").pack(anchor="w")
        self._lat_entry = ctk.CTkEntry(
            loc_card, textvariable=self._lat_var,
            placeholder_text="-7.952",
            font=("Segoe Mono", 13),
            fg_color="#1e293b", border_color="#334155",
        )
        self._lat_entry.pack(fill="x", pady=(2, 8))

        ctk.CTkLabel(loc_card, text="Longitude", font=("Segoe UI", 12), text_color="#94a3b8").pack(anchor="w")
        self._lon_entry = ctk.CTkEntry(
            loc_card, textvariable=self._lon_var,
            placeholder_text="-37.172",
            font=("Segoe Mono", 13),
            fg_color="#1e293b", border_color="#334155",
        )
        self._lon_entry.pack(fill="x", pady=(2, 8))

        ctk.CTkButton(
            loc_card,
            text="📡 Detectar Localização Automaticamente",
            command=self._auto_detect_location,
            fg_color="#1e3a5f", hover_color="#2563eb",
            font=("Segoe UI", 12),
        ).pack(fill="x", pady=(0, 4))

        ctk.CTkButton(
            loc_card,
            text="🔍 Testar API",
            command=self._test_api,
            fg_color="#1e293b", hover_color="#334155",
            font=("Segoe UI", 12),
        ).pack(fill="x")

        # ── Settings card ─────────────────────────────────────────
        set_card = self._card(parent, "⚙️ Configurações")

        ctk.CTkLabel(set_card, text="Intervalo de atualização (minutos)", font=("Segoe UI", 12), text_color="#94a3b8").pack(anchor="w")
        self._interval_var = ctk.StringVar()
        ctk.CTkEntry(
            set_card, textvariable=self._interval_var,
            placeholder_text="10",
            font=("Segoe Mono", 13),
            fg_color="#1e293b", border_color="#334155",
        ).pack(fill="x", pady=(2, 10))

        toggle_row = ctk.CTkFrame(set_card, fg_color="transparent")
        toggle_row.pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(toggle_row, text="Modo automático", font=("Segoe UI", 12), text_color="#94a3b8").pack(side="left")
        self._auto_switch = ctk.CTkSwitch(toggle_row, text="", command=self._toggle_auto)
        self._auto_switch.pack(side="right")

        startup_row = ctk.CTkFrame(set_card, fg_color="transparent")
        startup_row.pack(fill="x")
        ctk.CTkLabel(startup_row, text="Iniciar com Windows", font=("Segoe UI", 12), text_color="#94a3b8").pack(side="left")
        self._startup_switch = ctk.CTkSwitch(startup_row, text="", command=self._toggle_startup)
        self._startup_switch.pack(side="right")

        # ── Controls ──────────────────────────────────────────────
        ctrl_card = self._card(parent, "🎛️ Controles")

        btn_row1 = ctk.CTkFrame(ctrl_card, fg_color="transparent")
        btn_row1.pack(fill="x", pady=(0, 6))

        self._start_btn = ctk.CTkButton(
            btn_row1, text="▶ Iniciar",
            command=self._start,
            fg_color="#166534", hover_color="#16a34a",
            font=("Segoe UI", 13, "bold"),
        )
        self._start_btn.pack(side="left", expand=True, fill="x", padx=(0, 4))

        self._stop_btn = ctk.CTkButton(
            btn_row1, text="⏹ Parar",
            command=self._stop,
            fg_color="#7f1d1d", hover_color="#dc2626",
            font=("Segoe UI", 13, "bold"),
        )
        self._stop_btn.pack(side="right", expand=True, fill="x", padx=(4, 0))

        ctk.CTkButton(
            ctrl_card, text="🔄 Atualizar Agora",
            command=self._update_now,
            fg_color="#1e3a5f", hover_color="#2563eb",
            font=("Segoe UI", 13),
        ).pack(fill="x", pady=(0, 6))

        ctk.CTkButton(
            ctrl_card, text="💾 Salvar Configurações",
            command=self._save_settings,
            fg_color="#312e81", hover_color="#4338ca",
            font=("Segoe UI", 13),
        ).pack(fill="x")

        # ── Weather status ────────────────────────────────────────
        wx_card = self._card(parent, "🌡️ Clima Atual")
        self._weather_label = ctk.CTkLabel(
            wx_card,
            text="Aguardando dados...",
            font=("Segoe UI", 13),
            text_color="#94a3b8",
            wraplength=360,
        )
        self._weather_label.pack(anchor="w")

        # ── Wallpaper preview ─────────────────────────────────────
        prev_card = self._card(parent, "🖼️ Preview do Wallpaper")
        self._preview_label = ctk.CTkLabel(prev_card, text="Nenhum wallpaper ativo", font=("Segoe UI", 11), text_color="#475569")
        self._preview_label.pack()
        self._preview_img_label = ctk.CTkLabel(prev_card, text="")
        self._preview_img_label.pack()

    def _build_right(self, parent):
        """Right panel: wallpaper mapping per condition"""
        ctk.CTkLabel(
            parent,
            text="🗂️ Mapeamento Clima → Imagem",
            font=("Segoe UI", 15, "bold"),
            text_color="#e2e8f0",
        ).pack(anchor="w", padx=8, pady=(8, 4))

        ctk.CTkLabel(
            parent,
            text="Selecione uma imagem para cada condição climática",
            font=("Segoe UI", 11),
            text_color="#64748b",
        ).pack(anchor="w", padx=8, pady=(0, 12))

        ctk.CTkButton(
            parent,
            text="📁 Selecionar Pasta de Imagens",
            command=self._select_image_folder,
            fg_color="#1e293b", hover_color="#334155",
            font=("Segoe UI", 12),
        ).pack(fill="x", padx=8, pady=(0, 12))

        self._map_entries: dict[str, ctk.StringVar] = {}
        wallpaper_map = self.config_mgr.get_wallpaper_map()

        for key, label in CONDITION_KEYS:
            row = ctk.CTkFrame(parent, fg_color="#1a1a2e", corner_radius=8)
            row.pack(fill="x", padx=8, pady=3)

            ctk.CTkLabel(
                row, text=label,
                font=("Segoe UI", 12),
                text_color="#cbd5e1",
                width=200, anchor="w",
            ).pack(side="left", padx=(10, 4), pady=8)

            var = ctk.StringVar(value=wallpaper_map.get(key, ""))
            self._map_entries[key] = var

            ctk.CTkEntry(
                row, textvariable=var,
                font=("Segoe UI", 11),
                fg_color="#0f172a", border_color="#1e293b",
                width=160,
            ).pack(side="left", padx=4, expand=True, fill="x")

            ctk.CTkButton(
                row, text="...",
                width=36,
                command=lambda k=key, v=var: self._pick_image(k, v),
                fg_color="#1e293b", hover_color="#2563eb",
                font=("Segoe UI", 11),
            ).pack(side="right", padx=(4, 10))

    # ── Helpers ────────────────────────────────────────────────────

    def _card(self, parent, title: str) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(parent, fg_color="#111827", corner_radius=12)
        frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(
            frame, text=title,
            font=("Segoe UI", 13, "bold"),
            text_color="#e2e8f0",
        ).pack(anchor="w", padx=14, pady=(10, 6))
        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=(0, 12))
        return inner

    def _load_values(self):
        self._lat_var.set(str(self.config_mgr.latitude))
        self._lon_var.set(str(self.config_mgr.longitude))
        self._interval_var.set(str(self.config_mgr.update_interval_minutes))
        if self.config_mgr.auto_mode:
            self._auto_switch.select()
        else:
            self._auto_switch.deselect()
        if self.config_mgr.start_with_windows:
            self._startup_switch.select()
        else:
            self._startup_switch.deselect()

    # ── Event handlers ────────────────────────────────────────────

    def _start(self):
        self._save_settings(silent=True)
        self.scheduler.start()

    def _stop(self):
        self.scheduler.stop()

    def _update_now(self):
        self._save_settings(silent=True)
        self.scheduler.update_now()

    def _toggle_auto(self):
        self.config_mgr.auto_mode = bool(self._auto_switch.get())

    def _toggle_startup(self):
        from utils.startup_manager import set_startup
        enabled = bool(self._startup_switch.get())
        self.config_mgr.start_with_windows = enabled
        set_startup(enabled)

    def _save_settings(self, silent=False):
        try:
            lat = float(self._lat_var.get())
            lon = float(self._lon_var.get())
            interval = int(self._interval_var.get())
        except ValueError:
            if not silent:
                messagebox.showerror("Erro", "Latitude, longitude e intervalo devem ser números válidos.")
            return

        from utils.location_helper import validate_coordinates
        if not validate_coordinates(lat, lon):
            if not silent:
                messagebox.showerror("Erro", "Coordenadas fora do intervalo válido.\nLatitude: -90 a 90 | Longitude: -180 a 180")
            return

        if interval < 1:
            if not silent:
                messagebox.showerror("Erro", "Intervalo mínimo: 1 minuto.")
            return

        self.config_mgr.latitude = lat
        self.config_mgr.longitude = lon
        self.config_mgr.update_interval_minutes = interval

        # Save wallpaper map
        for key, var in self._map_entries.items():
            self.config_mgr.set_wallpaper_key(key, var.get())

        if not silent:
            messagebox.showinfo("Salvo", "Configurações salvas com sucesso!")

    def _auto_detect_location(self):
        def detect():
            from utils.location_helper import get_location_by_ip
            self._update_status_label("📡 Detectando localização...")
            result = get_location_by_ip()
            if result:
                lat, lon = result
                self._lat_var.set(str(lat))
                self._lon_var.set(str(lon))
                self._update_status_label(f"✅ Localização detectada: {lat}, {lon}")
            else:
                self._update_status_label("❌ Falha ao detectar localização")

        threading.Thread(target=detect, daemon=True).start()

    def _test_api(self):
        def test():
            from utils.location_helper import validate_coordinates
            from core.weather_api import fetch_weather
            from core.weather_mapper import describe_weather, get_wallpaper_key

            try:
                lat = float(self._lat_var.get())
                lon = float(self._lon_var.get())
            except ValueError:
                self.after(0, lambda: messagebox.showerror("Erro", "Informe coordenadas válidas primeiro."))
                return

            if not validate_coordinates(lat, lon):
                self.after(0, lambda: messagebox.showerror("Erro", "Coordenadas inválidas."))
                return

            self._update_status_label("🔍 Testando API...")
            weather = fetch_weather(lat, lon)
            if weather:
                key = get_wallpaper_key(weather)
                desc = describe_weather(weather)
                msg = f"✅ API OK!\n\n{desc}\n\nChave wallpaper: {key}"
                self.after(0, lambda: messagebox.showinfo("Teste da API", msg))
                self._update_status_label(f"✅ API OK • {desc}")
            else:
                self.after(0, lambda: messagebox.showerror("Falha", "❌ Não foi possível conectar à API.\nVerifique sua conexão."))
                self._update_status_label("❌ Falha na API")

        threading.Thread(target=test, daemon=True).start()

    def _pick_image(self, key: str, var: ctk.StringVar):
        path = filedialog.askopenfilename(
            title=f"Selecionar imagem para: {key}",
            filetypes=[("Imagens", "*.jpg *.jpeg *.png *.bmp"), ("Todos", "*.*")],
        )
        if path:
            var.set(path)
            self.config_mgr.set_wallpaper_key(key, path)

    def _select_image_folder(self):
        folder = filedialog.askdirectory(title="Selecionar pasta de imagens")
        if not folder:
            return
        # Auto-map files in folder by name pattern
        import os
        mapped = 0
        wallpaper_map = self.config_mgr.get_wallpaper_map()
        for key, _ in CONDITION_KEYS:
            for ext in (".jpg", ".jpeg", ".png", ".bmp"):
                candidate = os.path.join(folder, f"{key}{ext}")
                if os.path.exists(candidate):
                    self.config_mgr.set_wallpaper_key(key, candidate)
                    if key in self._map_entries:
                        self._map_entries[key].set(candidate)
                    mapped += 1
                    break
        if mapped > 0:
            messagebox.showinfo("Pasta de imagens", f"✅ {mapped} imagens mapeadas automaticamente!")
        else:
            messagebox.showinfo("Pasta de imagens", "Nenhuma imagem com nome compatível encontrada.\nNomeie as imagens como: clear_day.jpg, rain_night.png, etc.")

    def _on_scheduler_update(self):
        """Called from scheduler thread — must use after() to update UI."""
        self.after(0, self._refresh_ui)

    def _refresh_ui(self):
        status = self.scheduler.status
        weather = self.scheduler.last_weather
        image = self.scheduler.last_image

        # Status bar
        if "Erro" in status or "Falha" in status:
            color = "#ef4444"
            dot = "●"
        elif "Ativo" in status:
            color = "#22c55e"
            dot = "●"
        else:
            color = "#94a3b8"
            dot = "○"
        self._status_label.configure(text=f"{dot} {status}", text_color=color)

        # Weather info
        if weather:
            from core.weather_mapper import describe_weather, get_condition_emoji
            emoji = get_condition_emoji(weather)
            desc = describe_weather(weather)
            self._weather_label.configure(text=f"{emoji}  {desc}")

        # Preview
        if image and PIL_AVAILABLE:
            try:
                img = Image.open(image)
                img.thumbnail((320, 180))
                photo = ImageTk.PhotoImage(img)
                self._preview_img_label.configure(image=photo, text="")
                self._preview_img_label._photo = photo  # Prevent GC
                self._preview_label.configure(text=os.path.basename(image))
            except Exception as e:
                self._preview_label.configure(text=f"Erro ao carregar preview: {e}")
        elif image:
            self._preview_label.configure(text=os.path.basename(image))

    def _update_status_label(self, text: str):
        self.after(0, lambda: self._status_label.configure(text=text))

    def _on_close(self):
        """Minimize to tray instead of closing."""
        self.withdraw()
