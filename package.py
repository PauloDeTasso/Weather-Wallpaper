"""
Empacota a instalação do Weather Wallpaper.

O que faz:
  1. Gera dist/WeatherWallpaper.exe via PyInstaller (pula com --no-build)
  2. Copia images/ do repo para dist/images/ (pasta oficial da INSTALAÇÃO)
  3. Verifica o pacote final

Regra de distribuição: a instalação são 2 itens que andam juntos —
  WeatherWallpaper.exe + images/
Para instalar em outra máquina/pasta: copie os 2 para qualquer pasta.
O app procura fotos primeiro ao lado do .exe, depois dentro dele.
"""

import argparse
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_IMAGES = os.path.join(ROOT, "images")
DIST_DIR = os.path.join(ROOT, "dist")
DIST_EXE = os.path.join(DIST_DIR, "WeatherWallpaper.exe")
DIST_IMAGES = os.path.join(DIST_DIR, "images")


def run_build() -> None:
    cmd = [sys.executable, "-m", "PyInstaller", "-y", "WeatherWallpaper.spec"]
    print(f"[package] build: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=ROOT, check=True)


def sync_images() -> tuple[int, int]:
    """Copia images/ -> dist/images/. Retorna (copiados, total_bytes)."""
    if not os.path.isdir(SRC_IMAGES):
        raise SystemExit(f"[package] ERRO: pasta {SRC_IMAGES} não encontrada.")

    copied = 0
    total = 0
    for dirpath, _dirs, files in os.walk(SRC_IMAGES):
        rel = os.path.relpath(dirpath, SRC_IMAGES)
        dest_dir = os.path.join(DIST_IMAGES, rel) if rel != "." else DIST_IMAGES
        os.makedirs(dest_dir, exist_ok=True)
        for name in files:
            src = os.path.join(dirpath, name)
            dst = os.path.join(dest_dir, name)
            if not os.path.isfile(dst) or os.path.getmtime(src) > os.path.getmtime(dst):
                shutil.copy2(src, dst)
                copied += 1
            total += os.path.getsize(dst)
    return copied, total


def verify() -> None:
    errors: list[str] = []
    if not os.path.isfile(DIST_EXE):
        errors.append(f".exe não encontrado: {DIST_EXE}")
    if not os.path.isdir(DIST_IMAGES):
        errors.append(f"pasta de imagens não encontrada: {DIST_IMAGES}")
    else:
        n = sum(len(f) for _, _, f in os.walk(DIST_IMAGES))
        if n == 0:
            errors.append("dist/images está vazia!")
        else:
            print(f"[package] dist/images: {n} arquivos")
    if errors:
        raise SystemExit("[package] FALHOU:\n  - " + "\n  - ".join(errors))
    exe_mb = os.path.getsize(DIST_EXE) / 1e6
    print(f"[package] OK: {DIST_EXE} ({exe_mb:.0f} MB) + images/ ao lado")


def main() -> None:
    ap = argparse.ArgumentParser(description="Empacota a instalação (exe + images/).")
    ap.add_argument("--no-build", action="store_true",
                    help="pula o PyInstaller, só sincroniza images/ -> dist/images/")
    args = ap.parse_args()

    if not args.no_build:
        run_build()
    copied, total = sync_images()
    print(f"[package] imagens sincronizadas: {copied} copiadas, "
          f"{total / 1e6:.0f} MB em dist/images/")
    verify()
    print("[package] Instalar = copiar WeatherWallpaper.exe + images/ para a pasta destino.")


if __name__ == "__main__":
    main()
