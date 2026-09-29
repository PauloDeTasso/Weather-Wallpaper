# WeatherWallpaper.spec
# Arquivo de configuração do PyInstaller
# Execute com:  pyinstaller WeatherWallpaper.spec

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# ── Coleta extras do customtkinter (temas, fontes, imagens internas) ──
ctk_data = collect_data_files("customtkinter")

a = Analysis(
    ["main.py"],
    pathex=[os.path.abspath(".")],
    binaries=[],
    datas=[
        # Pasta de assets (imagens do usuário)
        ("assets", "assets"),
        # NOTA: images/ NÃO vai embutida de propósito — a instalação oficial
        # é exe + images/ lado a lado (fonte única, exe enxuto, boot rápido).
        # O app resolve fotos primeiro ao lado do .exe (ver utils/image_store).
        # Config padrão
        ("config.json", "."),
        # Temas e recursos internos do CustomTkinter
        *ctk_data,
    ],
    hiddenimports=[
        # CustomTkinter
        "customtkinter",
        # Pillow
        "PIL",
        "PIL.Image",
        "PIL.ImageTk",
        "PIL.ImageDraw",
        # pystray backends Windows
        "pystray._win32",
        # requests / urllib
        "requests",
        "urllib3",
        "charset_normalizer",
        "idna",
        "certifi",
        # tkinter
        "tkinter",
        "tkinter.filedialog",
        "tkinter.messagebox",
        # módulos do próprio projeto
        "core.weather_api",
        "core.weather_mapper",
        "core.wallpaper_controller",
        "core.scheduler",
        "ui.dashboard",
        "ui.tray",
        "utils.config_manager",
        "utils.location_helper",
        "utils.startup_manager",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Remove o que não precisa (reduz tamanho do .exe)
        "matplotlib",
        "numpy",
        "pandas",
        "scipy",
        "PyQt5",
        "PyQt6",
        "wx",
        "test",
        "unittest",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="WeatherWallpaper",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,            # comprime o .exe (instale UPX para ativar)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,       # ← SEM janela de console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon="assets/icon.ico",  # descomente se tiver um .ico
)
