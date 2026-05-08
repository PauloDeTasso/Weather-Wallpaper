"""
Dashboard — Weather Wallpaper App
UI moderna Windows 11 com CustomTkinter

Funcionalidades:
  • Painel de clima formatado com todos os dados da API
  • Indicador do wallpaper ativo (condição + período)
  • 66 botões individuais de seleção de imagem (11 condições × 6 períodos)
  • Sem renomeação manual — seleção e mapeamento automático
"""

import os
import threading
import logging
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import customtkinter as ctk
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    CTK = True
except ImportError:
    CTK = False

try:
    from PIL import Image, ImageTk
    PIL_OK = True
except ImportError:
    PIL_OK = False

from core.weather_mapper import (
    CONDITIONS, PERIODS,
    CONDITION_EMOJIS, PERIOD_EMOJIS,
    get_condition_label, get_period_label,
)

# ─────────────────────────────────────────────────────────────────────
# Paleta de cores
# ─────────────────────────────────────────────────────────────────────
BG        = "#0d1117"
BG2       = "#161b22"
BG3       = "#21262d"
ACCENT    = "#1f6feb"
ACCENT_H  = "#388bfd"
TXT       = "#e6edf3"
TXT2      = "#8b949e"
TXT3      = "#484f58"
GREEN     = "#3fb950"
RED       = "#f85149"
YELLOW    = "#d29922"
PURPLE    = "#8b5cf6"

# ─────────────────────────────────────────────────────────────────────
# Cores de período (badge)
# ─────────────────────────────────────────────────────────────────────
PERIOD_COLORS = {
    "dawn":      ("#f97316", "#431407"),
    "morning":   ("#fbbf24", "#451a03"),
    "afternoon": ("#34d399", "#064e3b"),
    "dusk":      ("#f43f5e", "#4c0519"),
    "night":     ("#818cf8", "#1e1b4b"),
    "midnight":  ("#38bdf8", "#0c2a3e"),
}

# Cores de condição (badge)
COND_COLORS = {
    "clear":         ("#fde68a", "#3d2e05"),
    "partly_cloudy": ("#a5b4fc", "#1e1b4b"),
    "cloudy":        ("#94a3b8", "#1e2535"),
    "rain":          ("#60a5fa", "#0c1a3a"),
    "storm":         ("#c084fc", "#2d0a4e"),
    "post_rain":     ("#34d399", "#022c22"),
    "fog":           ("#cbd5e1", "#1e293b"),
    "snow":          ("#bae6fd", "#082f49"),
    "windy":         ("#86efac", "#052e16"),
    "cold":          ("#7dd3fc", "#0c1a3e"),
    "hot":           ("#fb923c", "#431407"),
}

Base = (ctk.CTk if CTK else tk.Tk)


class Dashboard(Base):
    def __init__(self, config, scheduler, tray=None):
        super().__init__()
        self.config_mgr = config
        self.scheduler = scheduler
        self.tray = tray
        self._preview_photo = None

        if tray:
            tray.set_dashboard(self)

        self.scheduler.add_callback(self._on_update)

        self._setup_window()
        self._build_ui()
        self._load_form_values()

        self.scheduler.start()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ─────────────────────────────────────────────────────────────
    # Janela
    # ─────────────────────────────────────────────────────────────

    def _setup_window(self):
        self.title("Weather Wallpaper  •  Windows 11")
        self.geometry("1180x820")
        self.minsize(1000, 700)
        if CTK:
            self.configure(fg_color=BG)

    # ─────────────────────────────────────────────────────────────
    # Layout principal
    # ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Top bar ──────────────────────────────────────────────
        top = ctk.CTkFrame(self, fg_color=BG2, corner_radius=0, height=56)
        top.pack(fill="x")
        top.pack_propagate(False)

        ctk.CTkLabel(
            top, text="🌤  Weather Wallpaper",
            font=("Segoe UI", 20, "bold"), text_color=TXT,
        ).pack(side="left", padx=20)

        self._topbar_status = ctk.CTkLabel(
            top, text="○  Iniciando...",
            font=("Segoe UI", 12), text_color=TXT3,
        )
        self._topbar_status.pack(side="right", padx=20)

        # ── Tab view ─────────────────────────────────────────────
        self._tabs = ctk.CTkTabview(self, fg_color=BG, segmented_button_fg_color=BG2,
                                    segmented_button_selected_color=ACCENT,
                                    segmented_button_selected_hover_color=ACCENT_H,
                                    segmented_button_unselected_color=BG2,
                                    segmented_button_unselected_hover_color=BG3,
                                    text_color=TXT, text_color_disabled=TXT2)
        self._tabs.pack(fill="both", expand=True, padx=12, pady=(6, 12))

        self._tabs.add("🌡️  Clima & Status")
        self._tabs.add("🖼️  Imagens por Condição")
        self._tabs.add("⚙️  Configurações")

        self._build_tab_status(self._tabs.tab("🌡️  Clima & Status"))
        self._build_tab_images(self._tabs.tab("🖼️  Imagens por Condição"))
        self._build_tab_settings(self._tabs.tab("⚙️  Configurações"))

    # ─────────────────────────────────────────────────────────────
    # ABA 1 — Clima & Status
    # ─────────────────────────────────────────────────────────────

    def _build_tab_status(self, tab):
        tab.configure(fg_color=BG)
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=0)
        tab.grid_rowconfigure(1, weight=1)

        # ── Wallpaper ativo (topo, largura total) ─────────────────
        active_frame = ctk.CTkFrame(tab, fg_color=BG2, corner_radius=12)
        active_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=4, pady=(4, 8))

        ctk.CTkLabel(active_frame, text="🖼️  WALLPAPER ATIVO AGORA",
                     font=("Segoe UI", 11, "bold"), text_color=TXT3).pack(anchor="w", padx=16, pady=(10, 0))

        active_body = ctk.CTkFrame(active_frame, fg_color="transparent")
        active_body.pack(fill="x", padx=16, pady=(4, 12))

        # Lado esquerdo: info
        active_info = ctk.CTkFrame(active_body, fg_color="transparent")
        active_info.pack(side="left", fill="x", expand=True)

        self._active_cond_label = ctk.CTkLabel(
            active_info, text="—",
            font=("Segoe UI", 26, "bold"), text_color=TXT,
        )
        self._active_cond_label.pack(anchor="w")

        self._active_period_label = ctk.CTkLabel(
            active_info, text="—",
            font=("Segoe UI", 14), text_color=TXT2,
        )
        self._active_period_label.pack(anchor="w")

        self._active_file_label = ctk.CTkLabel(
            active_info, text="Nenhum wallpaper ativo",
            font=("Segoe UI", 11), text_color=TXT3,
        )
        self._active_file_label.pack(anchor="w", pady=(4, 0))

        # Lado direito: preview thumbnail
        self._preview_widget = ctk.CTkLabel(active_body, text="", width=213, height=120)
        self._preview_widget.pack(side="right", padx=(16, 0))

        # ── Painel de dados da API ────────────────────────────────
        weather_frame = ctk.CTkFrame(tab, fg_color=BG2, corner_radius=12)
        weather_frame.grid(row=1, column=0, sticky="nsew", padx=(4, 6), pady=0)

        ctk.CTkLabel(weather_frame, text="🌐  DADOS DA API  ( Open-Meteo )",
                     font=("Segoe UI", 11, "bold"), text_color=TXT3).pack(anchor="w", padx=16, pady=(12, 6))

        self._weather_card_frame = ctk.CTkScrollableFrame(
            weather_frame, fg_color="transparent", corner_radius=0,
        )
        self._weather_card_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self._weather_rows: dict[str, ctk.CTkLabel] = {}
        self._build_weather_card_rows()

        # ── Controles rápidos ─────────────────────────────────────
        ctrl_frame = ctk.CTkFrame(tab, fg_color=BG2, corner_radius=12)
        ctrl_frame.grid(row=1, column=1, sticky="nsew", padx=(6, 4), pady=0)

        ctk.CTkLabel(ctrl_frame, text="🎛️  CONTROLES",
                     font=("Segoe UI", 11, "bold"), text_color=TXT3).pack(anchor="w", padx=16, pady=(12, 8))

        def btn(parent, text, cmd, color, hover):
            return ctk.CTkButton(
                parent, text=text, command=cmd,
                fg_color=color, hover_color=hover,
                font=("Segoe UI", 13, "bold"), height=40, corner_radius=8,
            )

        btn(ctrl_frame, "▶  Iniciar",        self._start,       "#1a4731", GREEN).pack(fill="x", padx=16, pady=(0, 6))
        btn(ctrl_frame, "⏹  Parar",          self._stop,        "#4a0f0f", RED).pack(fill="x", padx=16, pady=(0, 6))
        btn(ctrl_frame, "🔄  Atualizar Agora",self._update_now,  ACCENT,    ACCENT_H).pack(fill="x", padx=16, pady=(0, 16))

        sep = ctk.CTkFrame(ctrl_frame, fg_color=BG3, height=1)
        sep.pack(fill="x", padx=16, pady=(0, 12))

        ctk.CTkLabel(ctrl_frame, text="⏱️  Próxima atualização em:",
                     font=("Segoe UI", 11), text_color=TXT2).pack(anchor="w", padx=16)
        self._countdown_label = ctk.CTkLabel(
            ctrl_frame, text="—",
            font=("Segoe UI", 22, "bold"), text_color=ACCENT,
        )
        self._countdown_label.pack(anchor="w", padx=16, pady=(2, 12))

        sep2 = ctk.CTkFrame(ctrl_frame, fg_color=BG3, height=1)
        sep2.pack(fill="x", padx=16, pady=(0, 12))

        ctk.CTkLabel(ctrl_frame, text="🕐  Última atualização:",
                     font=("Segoe UI", 11), text_color=TXT2).pack(anchor="w", padx=16)
        self._last_update_label = ctk.CTkLabel(
            ctrl_frame, text="—",
            font=("Segoe UI", 13), text_color=TXT,
        )
        self._last_update_label.pack(anchor="w", padx=16, pady=(2, 0))

        # Inicia contador
        self._start_countdown()

    def _build_weather_card_rows(self):
        """Cria as linhas do painel de dados (preenchidas depois com _refresh_weather_card)."""
        rows_def = [
            ("condition",       "🌤  Condição"),
            ("weathercode",     "🔢  Código WMO"),
            ("weathercode_label","📋  Descrição oficial"),
            ("period",          "🕐  Período do dia"),
            ("temperature",     "🌡️  Temperatura"),
            ("feels_like",      "🤔  Sensação térmica"),
            ("windspeed",       "💨  Velocidade do vento"),
            ("wind_label",      "📊  Intensidade do vento"),
            ("winddirection",   "🧭  Direção do vento"),
            ("is_day",          "🌞/🌙  Dia ou noite"),
            ("api_time",        "🕰️  Horário da leitura"),
            ("wallpaper_key",   "🖼️  Chave do wallpaper"),
        ]
        for i, (field, label) in enumerate(rows_def):
            row_bg = BG3 if i % 2 == 0 else "transparent"
            row = ctk.CTkFrame(self._weather_card_frame, fg_color=row_bg, corner_radius=6)
            row.pack(fill="x", pady=1)

            ctk.CTkLabel(
                row, text=label,
                font=("Segoe UI", 12), text_color=TXT2,
                width=220, anchor="w",
            ).pack(side="left", padx=(10, 4), pady=7)

            val_lbl = ctk.CTkLabel(
                row, text="—",
                font=("Segoe UI", 12, "bold"), text_color=TXT,
                anchor="w",
            )
            val_lbl.pack(side="left", fill="x", expand=True, padx=(0, 10))
            self._weather_rows[field] = val_lbl

    # ─────────────────────────────────────────────────────────────
    # ABA 2 — Imagens por condição
    # ─────────────────────────────────────────────────────────────

    def _build_tab_images(self, tab):
        tab.configure(fg_color=BG)

        # Header
        hdr = ctk.CTkFrame(tab, fg_color=BG2, corner_radius=10)
        hdr.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            hdr,
            text="Selecione uma imagem para cada combinação  Condição × Período  clicando em  📂 Escolher",
            font=("Segoe UI", 12), text_color=TXT2,
        ).pack(side="left", padx=14, pady=10)

        ctk.CTkLabel(
            hdr, text="✅ arquivo ok    ❌ não encontrado",
            font=("Segoe UI", 11), text_color=TXT3,
        ).pack(side="right", padx=14)

        # Scrollable body
        body = ctk.CTkScrollableFrame(tab, fg_color=BG, corner_radius=0)
        body.pack(fill="both", expand=True)

        self._map_vars: dict[str, tk.StringVar] = {}
        self._map_status_lbls: dict[str, ctk.CTkLabel] = {}
        self._map_name_lbls: dict[str, ctk.CTkLabel] = {}

        wallpaper_map = self.config_mgr.get_wallpaper_map()

        for cond_key, cond_name in CONDITIONS:
            # ── Cabeçalho da condição ─────────────────────────────
            cond_fg, cond_bg = COND_COLORS.get(cond_key, (TXT, BG3))
            cond_hdr = ctk.CTkFrame(body, fg_color=cond_bg, corner_radius=8)
            cond_hdr.pack(fill="x", padx=4, pady=(10, 2))

            emoji = CONDITION_EMOJIS.get(cond_key, "🌡️")
            ctk.CTkLabel(
                cond_hdr,
                text=f"{emoji}  {cond_name.upper()}",
                font=("Segoe UI", 13, "bold"),
                text_color=cond_fg,
            ).pack(anchor="w", padx=14, pady=7)

            # ── Linhas de período ─────────────────────────────────
            for period_key, period_name, _ in PERIODS:
                key = f"{cond_key}_{period_key}"
                path = wallpaper_map.get(key, "")
                p_txt, p_bg = PERIOD_COLORS.get(period_key, (TXT, BG3))
                p_emoji = PERIOD_EMOJIS.get(period_key, "🕐")
                self._build_image_row(body, key, cond_key, period_key,
                                      period_name, p_emoji, p_txt, p_bg, path)

    def _build_image_row(self, parent, key, cond_key, period_key,
                         period_name, p_emoji, p_txt, p_bg, current_path):
        """Uma linha: [período] [nome do arquivo / placeholder] [✅❌] [📂 Escolher] [✖]"""

        row = ctk.CTkFrame(parent, fg_color=BG2, corner_radius=6)
        row.pack(fill="x", padx=4, pady=1)

        # Badge de período
        badge = ctk.CTkLabel(
            row, text=f"  {p_emoji} {period_name}  ",
            font=("Segoe UI", 11, "bold"),
            text_color=p_txt, fg_color=p_bg,
            corner_radius=5, width=130,
        )
        badge.pack(side="left", padx=(10, 8), pady=8)

        # Nome do arquivo (label, não entry — mais limpo visualmente)
        var = tk.StringVar(value=current_path)
        self._map_vars[key] = var

        name_lbl = ctk.CTkLabel(
            row,
            text=self._short_path(current_path),
            font=("Segoe UI", 11),
            text_color=TXT if current_path else TXT3,
            anchor="w",
        )
        name_lbl.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._map_name_lbls[key] = name_lbl

        # Ícone de status
        icon = self._status_icon(current_path)
        status_lbl = ctk.CTkLabel(row, text=icon, font=("Segoe UI", 14), width=28)
        status_lbl.pack(side="left", padx=(0, 6))
        self._map_status_lbls[key] = status_lbl

        # Botão Escolher
        ctk.CTkButton(
            row,
            text="📂  Escolher",
            width=110, height=30,
            command=lambda k=key, v=var: self._pick_image(k, v),
            fg_color=ACCENT, hover_color=ACCENT_H,
            font=("Segoe UI", 11, "bold"), corner_radius=6,
        ).pack(side="left", padx=(0, 4), pady=8)

        # Botão Limpar
        ctk.CTkButton(
            row,
            text="✖",
            width=30, height=30,
            command=lambda k=key, v=var: self._clear_image(k, v),
            fg_color="#2d0f0f", hover_color=RED,
            font=("Segoe UI", 12, "bold"), corner_radius=6,
        ).pack(side="left", padx=(0, 10), pady=8)

    # ─────────────────────────────────────────────────────────────
    # ABA 3 — Configurações
    # ─────────────────────────────────────────────────────────────

    def _build_tab_settings(self, tab):
        tab.configure(fg_color=BG)

        scroll = ctk.CTkScrollableFrame(tab, fg_color=BG, corner_radius=0)
        scroll.pack(fill="both", expand=True)

        # ── Localização ──────────────────────────────────────────
        loc = self._card(scroll, "📍  Localização GPS")

        self._lat_var = tk.StringVar()
        self._lon_var = tk.StringVar()

        self._field(loc, "Latitude", self._lat_var, "-7.952 (ex: Patos - PB)")
        self._field(loc, "Longitude", self._lon_var, "-37.172")

        ctk.CTkButton(
            loc, text="📡  Detectar Minha Localização Automaticamente (via IP)",
            command=self._auto_detect,
            fg_color="#1a3a5c", hover_color=ACCENT,
            font=("Segoe UI", 12), height=36,
        ).pack(fill="x", pady=(0, 4))

        ctk.CTkButton(
            loc, text="🔍  Testar Conexão com a API de Clima",
            command=self._test_api,
            fg_color=BG3, hover_color=BG2,
            font=("Segoe UI", 12), height=36,
        ).pack(fill="x")

        # ── Atualização ──────────────────────────────────────────
        upd = self._card(scroll, "⏱️  Atualização Automática")
        self._interval_var = tk.StringVar()
        self._field(upd, "Intervalo de atualização (em minutos)", self._interval_var, "10")

        row_auto = ctk.CTkFrame(upd, fg_color="transparent")
        row_auto.pack(fill="x", pady=3)
        ctk.CTkLabel(row_auto, text="Modo automático (troca de wallpaper automática)",
                     font=("Segoe UI", 12), text_color=TXT2).pack(side="left")
        self._auto_sw = ctk.CTkSwitch(row_auto, text="", command=self._toggle_auto)
        self._auto_sw.pack(side="right")

        row_startup = ctk.CTkFrame(upd, fg_color="transparent")
        row_startup.pack(fill="x", pady=3)
        ctk.CTkLabel(row_startup, text="Iniciar com Windows (ao ligar o PC)",
                     font=("Segoe UI", 12), text_color=TXT2).pack(side="left")
        self._startup_sw = ctk.CTkSwitch(row_startup, text="", command=self._toggle_startup)
        self._startup_sw.pack(side="right")

        # ── Salvar ───────────────────────────────────────────────
        save_area = ctk.CTkFrame(scroll, fg_color="transparent")
        save_area.pack(fill="x", pady=(8, 0))

        ctk.CTkButton(
            save_area, text="💾  Salvar Todas as Configurações",
            command=self._save_settings,
            fg_color="#2d1b69", hover_color=PURPLE,
            font=("Segoe UI", 13, "bold"), height=42, corner_radius=10,
        ).pack(fill="x")

    # ─────────────────────────────────────────────────────────────
    # Helpers de UI
    # ─────────────────────────────────────────────────────────────

    def _card(self, parent, title: str) -> ctk.CTkFrame:
        outer = ctk.CTkFrame(parent, fg_color=BG2, corner_radius=10)
        outer.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(outer, text=title, font=("Segoe UI", 13, "bold"), text_color=TXT).pack(
            anchor="w", padx=14, pady=(10, 4))
        inner = ctk.CTkFrame(outer, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=(0, 12))
        return inner

    def _field(self, parent, label: str, var: tk.StringVar, placeholder: str):
        ctk.CTkLabel(parent, text=label, font=("Segoe UI", 11), text_color=TXT2).pack(anchor="w")
        ctk.CTkEntry(
            parent, textvariable=var,
            placeholder_text=placeholder,
            font=("Segoe Mono", 12),
            fg_color="#0d1117", border_color=BG3, height=32,
        ).pack(fill="x", pady=(2, 8))

    def _short_path(self, path: str) -> str:
        if not path:
            return "  Nenhuma imagem selecionada"
        name = os.path.basename(path)
        return f"  {name}"

    def _status_icon(self, path: str) -> str:
        if not path:
            return "  "
        return "✅" if os.path.isfile(path) else "❌"

    def _load_form_values(self):
        self._lat_var.set(str(self.config_mgr.latitude))
        self._lon_var.set(str(self.config_mgr.longitude))
        self._interval_var.set(str(self.config_mgr.update_interval_minutes))
        if self.config_mgr.auto_mode:
            self._auto_sw.select()
        else:
            self._auto_sw.deselect()
        if self.config_mgr.start_with_windows:
            self._startup_sw.select()
        else:
            self._startup_sw.deselect()

    # ─────────────────────────────────────────────────────────────
    # Countdown timer
    # ─────────────────────────────────────────────────────────────

    def _start_countdown(self):
        self._next_update_ts: float = 0
        self._tick_countdown()

    def _tick_countdown(self):
        try:
            import time
            now = time.time()
            if self.scheduler.is_running and self._next_update_ts > now:
                remaining = int(self._next_update_ts - now)
                mins, secs = divmod(remaining, 60)
                self._countdown_label.configure(text=f"{mins:02d}:{secs:02d}")
            elif self.scheduler.is_running:
                self._countdown_label.configure(text="—")
            else:
                self._countdown_label.configure(text="Parado")
        except Exception:
            pass
        self.after(1000, self._tick_countdown)

    # ─────────────────────────────────────────────────────────────
    # Actions
    # ─────────────────────────────────────────────────────────────

    def _start(self):
        self._save_settings(silent=True)
        self.scheduler.start()
        self._tabs.set("🌡️  Clima & Status")

    def _stop(self):
        self.scheduler.stop()

    def _update_now(self):
        self._save_settings(silent=True)
        self.scheduler.update_now()

    def _toggle_auto(self):
        self.config_mgr.auto_mode = bool(self._auto_sw.get())

    def _toggle_startup(self):
        from utils.startup_manager import set_startup
        v = bool(self._startup_sw.get())
        self.config_mgr.start_with_windows = v
        set_startup(v)

    def _save_settings(self, silent: bool = False):
        try:
            lat = float(self._lat_var.get().replace(",", "."))
            lon = float(self._lon_var.get().replace(",", "."))
            interval = int(self._interval_var.get())
        except ValueError:
            if not silent:
                messagebox.showerror("Erro de validação", "⚠️  Latitude, longitude e intervalo devem ser números válidos.")
            return False

        from utils.location_helper import validate_coordinates
        if not validate_coordinates(lat, lon):
            if not silent:
                messagebox.showerror("Coordenadas inválidas",
                                     "Latitude deve estar entre -90 e 90\nLongitude deve estar entre -180 e 180")
            return False

        if interval < 1:
            if not silent:
                messagebox.showerror("Intervalo inválido", "O intervalo mínimo é 1 minuto.")
            return False

        self.config_mgr.latitude = lat
        self.config_mgr.longitude = lon
        self.config_mgr.update_interval_minutes = interval

        # Save image map
        for key, var in self._map_vars.items():
            self.config_mgr.set_wallpaper_key(key, var.get())

        if not silent:
            messagebox.showinfo("Configurações salvas", "✅  Todas as configurações foram salvas com sucesso!")
        return True

    def _pick_image(self, key: str, var: tk.StringVar):
        """Abre o explorador de arquivos do Windows para escolher qualquer imagem."""
        current = var.get()
        init_dir = os.path.dirname(current) if current and os.path.isdir(os.path.dirname(current)) else os.path.expanduser("~")

        path = filedialog.askopenfilename(
            title=f"Escolher imagem para  →  {key}",
            initialdir=init_dir,
            filetypes=[
                ("Imagens",         "*.jpg *.jpeg *.png *.bmp *.webp"),
                ("JPEG",            "*.jpg *.jpeg"),
                ("PNG",             "*.png"),
                ("Bitmap",          "*.bmp"),
                ("Todos os arquivos", "*.*"),
            ],
        )
        if path:
            path = os.path.normpath(path)
            var.set(path)
            self.config_mgr.set_wallpaper_key(key, path)
            # Update UI labels
            lbl = self._map_name_lbls.get(key)
            if lbl:
                lbl.configure(text=self._short_path(path), text_color=TXT)
            icon_lbl = self._map_status_lbls.get(key)
            if icon_lbl:
                icon_lbl.configure(text=self._status_icon(path))
            logger.info(f"Image set: {key} → {path}")

    def _clear_image(self, key: str, var: tk.StringVar):
        var.set("")
        self.config_mgr.set_wallpaper_key(key, "")
        lbl = self._map_name_lbls.get(key)
        if lbl:
            lbl.configure(text="  Nenhuma imagem selecionada", text_color=TXT3)
        icon_lbl = self._map_status_lbls.get(key)
        if icon_lbl:
            icon_lbl.configure(text="  ")

    def _auto_detect(self):
        def run():
            from utils.location_helper import get_location_by_ip
            self._set_topbar("📡  Detectando localização...")
            result = get_location_by_ip()
            if result:
                lat, lon = result
                self.after(0, lambda: self._lat_var.set(str(lat)))
                self.after(0, lambda: self._lon_var.set(str(lon)))
                self._set_topbar(f"✅  Localização: {lat}, {lon}")
                self.after(0, lambda: messagebox.showinfo(
                    "Localização detectada",
                    f"✅  Localização obtida com sucesso!\n\nLatitude:   {lat}\nLongitude:  {lon}\n\nClique em Salvar para confirmar."
                ))
            else:
                self._set_topbar("❌  Falha ao detectar localização")
        threading.Thread(target=run, daemon=True).start()

    def _test_api(self):
        def run():
            from utils.location_helper import validate_coordinates
            from core.weather_api import fetch_weather
            from core.weather_mapper import get_weather_card_data
            try:
                lat = float(self._lat_var.get().replace(",", "."))
                lon = float(self._lon_var.get().replace(",", "."))
            except ValueError:
                self.after(0, lambda: messagebox.showerror("Erro", "Informe coordenadas válidas."))
                return
            if not validate_coordinates(lat, lon):
                self.after(0, lambda: messagebox.showerror("Erro", "Coordenadas fora do intervalo."))
                return

            self._set_topbar("🔍  Testando API...")
            w = fetch_weather(lat, lon)
            if w:
                d = get_weather_card_data(w)
                msg = (
                    f"✅  API respondeu com sucesso!\n\n"
                    f"🌤  Condição:       {d['condition_label']}\n"
                    f"🕐  Período:        {d['period_label']}\n"
                    f"🌡️  Temperatura:    {d['temperature']}°C\n"
                    f"💨  Vento:          {d['windspeed']} km/h ({d['wind_label']})\n"
                    f"🧭  Direção:        {d['wind_dir_text']}\n"
                    f"🖼️  Chave wallpaper: {d['wallpaper_key']}"
                )
                self.after(0, lambda: messagebox.showinfo("Teste da API", msg))
                self._set_topbar(f"✅  API OK  —  {d['condition_label']}  {d['temperature']}°C")
            else:
                self.after(0, lambda: messagebox.showerror(
                    "Falha na API",
                    "❌  Não foi possível conectar à API Open-Meteo.\n\nVerifique sua conexão com a internet."
                ))
                self._set_topbar("❌  Falha na API")
        threading.Thread(target=run, daemon=True).start()

    # ─────────────────────────────────────────────────────────────
    # Scheduler callback → refresh UI
    # ─────────────────────────────────────────────────────────────

    def _on_update(self):
        """Chamado pela thread do scheduler — usa after() para thread-safety."""
        import time
        self._next_update_ts = time.time() + self.config_mgr.update_interval_minutes * 60
        self.after(0, self._refresh_ui)

    def _refresh_ui(self):
        status = self.scheduler.status
        data = self.scheduler.last_weather_data
        image = self.scheduler.last_image
        key = self.scheduler.last_key

        # ── Top bar status ────────────────────────────────────────
        if "❌" in status or "Erro" in status:
            color = RED
        elif "✅" in status or "Ativo" in status:
            color = GREEN
        elif "⚠️" in status:
            color = YELLOW
        else:
            color = TXT3

        self._topbar_status.configure(text=status, text_color=color)

        # Última atualização
        self._last_update_label.configure(
            text=datetime.now().strftime("%d/%m/%Y  %H:%M:%S"), text_color=TXT
        )

        # ── Wallpaper ativo ───────────────────────────────────────
        if key and data:
            cond_emoji = data.get("condition_emoji", "🌡️")
            cond_label = data.get("condition_label", "—")
            period_emoji = data.get("period_emoji", "🕐")
            period_label = data.get("period_label", "—")

            self._active_cond_label.configure(
                text=f"{cond_emoji}  {cond_label}",
                text_color=COND_COLORS.get(data.get("condition_key", "clear"), (TXT, BG3))[0]
            )
            self._active_period_label.configure(
                text=f"{period_emoji}  {period_label}",
                text_color=PERIOD_COLORS.get(data.get("period_key", "morning"), (TXT, BG3))[0]
            )

        if image:
            self._active_file_label.configure(
                text=f"📄  {os.path.basename(image)}  —  {image}", text_color=TXT3
            )

        # ── Preview ───────────────────────────────────────────────
        if image and PIL_OK and os.path.isfile(image):
            try:
                img = Image.open(image)
                img.thumbnail((213, 120))
                photo = ImageTk.PhotoImage(img)
                self._preview_photo = photo
                self._preview_widget.configure(image=photo, text="")
            except Exception:
                self._preview_widget.configure(image=None, text="(preview indisponível)")
        elif not image:
            self._preview_widget.configure(image=None, text="Sem imagem")

        # ── Painel de dados da API ────────────────────────────────
        if data:
            self._fill_weather_card(data)

    def _fill_weather_card(self, d: dict):
        """Preenche as linhas do painel de dados com os valores formatados."""
        updates = {
            "condition":        f"{d['condition_emoji']}  {d['condition_label']}",
            "weathercode":      f"{d['weathercode']}",
            "weathercode_label":f"{d['weathercode_label']}",
            "period":           f"{d['period_emoji']}  {d['period_label']}  ({datetime.now().strftime('%H:%M')})",
            "temperature":      f"{d['temperature']} °C",
            "feels_like":       f"{d['feels_like']} °C",
            "windspeed":        f"{d['windspeed']} km/h",
            "wind_label":       f"{d['wind_label']}",
            "winddirection":    f"{d['winddirection']}°  ({d['wind_dir_text']})",
            "is_day":           "☀️  Dia" if d['is_day'] else "🌙  Noite",
            "api_time":         d.get("api_time", "—"),
            "wallpaper_key":    d.get("wallpaper_key", "—"),
        }
        for field, value in updates.items():
            lbl = self._weather_rows.get(field)
            if lbl:
                lbl.configure(text=value)

    def _set_topbar(self, text: str):
        self.after(0, lambda: self._topbar_status.configure(text=text))

    def _on_close(self):
        self.withdraw()
