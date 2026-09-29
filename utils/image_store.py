"""
Image Store — fonte oficial de wallpapers por convenção de pasta + nome.

Estrutura canônica (escolhida pelo usuário: pastas em inglês + nome exato):

    images/<condition>/<period>.<ext>
    assets/<condition>/<period>.<ext>   (fallback legado)

    Ex: images/rain/morning.jpg
        images/clear/dawn.png

Para trocar uma foto: copie a nova para a pasta da condição
com o MESMO nome do período (ex: morning.jpg) — sobrescreve e pronto.
Na próxima atualização o sistema usa automaticamente, sem clicar em nada.

Compat retro (ainda aceito, menor prioridade):
    images/<condition>_<period>.<ext>   (flat)
    assets/<condition>_<period>.<ext>   (flat, default antigo do config.json)

Override manual (aba "Imagens por Condição" → 📂 Escolher):
    se o path salvo no config for diferente do path automático (e existir),
    o manual vence e a origem é 'manual'. Caso contrário origem é 'auto'.

Extensões aceitas (mesmas do wallpaper_controller): .jpg .jpeg .png .bmp
"""

import os
import sys
import logging

logger = logging.getLogger(__name__)

CONDITIONS = [
    "clear", "partly_cloudy", "cloudy", "rain",
    "storm", "post_rain", "fog", "snow", "windy", "cold", "hot",
]
PERIODS = ["dawn", "morning", "afternoon", "dusk", "night", "midnight"]

EXTS = (".jpg", ".jpeg", ".png", ".bmp")

# Pastas base escaneadas, em ordem de prioridade
BASE_DIRS = ("images", "assets")


def _search_bases() -> list[str]:
    """
    Pastas-base procuradas, em ordem de prioridade:
      1. Pasta do .exe (portátil — é AQUI que o usuário copia/sobrescreve fotos)
      2. %APPDATA%/WeatherWallpaper (sempre gravável)
      3. Bundle interno do PyInstaller (_MEIPASS, somente leitura)
      4. Diretório atual (modo dev)
    """
    bases: list[str] = []
    if getattr(sys, "frozen", False):
        bases.append(os.path.dirname(os.path.abspath(sys.executable)))
    else:
        bases.append(os.getcwd())
    try:
        import builtins
        d = getattr(builtins, "APP_USER_DATA_DIR", "")
        if d and os.path.isdir(d):
            bases.append(d)
    except Exception:
        pass
    try:
        import builtins
        rp = getattr(builtins, "APP_RESOURCE_PATH", None)
        if rp:
            b = rp(".")
            if os.path.isdir(b):
                bases.append(b)
    except Exception:
        pass
    if os.getcwd() not in bases:
        bases.append(os.getcwd())
    # dedupe mantendo ordem
    seen: list[str] = []
    for b in bases:
        nb = os.path.normcase(os.path.abspath(b))
        if not any(os.path.normcase(os.path.abspath(s)) == nb for s in seen):
            seen.append(b)
    return seen


def _resource_base() -> str:
    """Mantido por compat: primeira base de busca."""
    return _search_bases()[0]


def expected_relative_path(condition: str, period: str, ext: str = ".jpg") -> str:
    """Caminho canônico relativo: images/<condition>/<period>.<ext>"""
    return os.path.join("images", condition, f"{period}{ext}")


def _candidate_paths(base: str, condition: str, period: str) -> list[str]:
    """Todos os caminhos candidatos para um slot, em ordem de prioridade."""
    cands: list[str] = []
    for basedir in BASE_DIRS:
        root = os.path.join(base, basedir, condition)
        for ext in EXTS:
            cands.append(os.path.join(root, f"{period}{ext}"))
    # flat legado: <base>/images/clear_morning.jpg , <base>/assets/clear_morning.jpg
    for basedir in BASE_DIRS:
        for ext in EXTS:
            cands.append(os.path.join(base, basedir, f"{condition}_{period}{ext}"))
    return cands


def find_auto_image(condition: str, period: str) -> str | None:
    """Retorna o caminho absoluto da foto automática do slot, ou None."""
    for base in _search_bases():
        for path in _candidate_paths(base, condition, period):
            if os.path.isfile(path):
                return os.path.abspath(path)
    return None


def resolve_image(key: str, manual_path: str = "") -> tuple[str | None, str]:
    """
    Resolve a imagem final de um slot.

    Retorna (path_ou_None, origem) onde origem ∈ {'manual','auto','missing'}.
    - 'manual': path do config existe e é diferente do auto → respeita usuário
    - 'auto':   foto encontrada por convenção de pasta/nome
    - 'missing': nada encontrado
    """
    parts = key.rsplit("_", 1)
    if len(parts) != 2:
        return None, "missing"
    cond, period = parts

    auto = find_auto_image(cond, period)

    manual = (manual_path or "").strip()
    if "_MEI" in manual.upper():
        # Temp obsoleta de bundle antigo (processo morto sem limpar) — ignora
        logger.warning(f"[{key}] ignorando path obsoleto de bundle antigo.")
        manual = ""
    if manual and os.path.isfile(manual):
        abs_manual = os.path.abspath(manual)
        if auto and os.path.abspath(auto) == abs_manual:
            return auto, "auto"  # manual aponta p/ o mesmo arquivo = auto
        return abs_manual, "manual"

    if auto:
        return auto, "auto"
    # manual salvo mas arquivo sumiu → tenta auto mesmo assim (já None aqui)
    return None, "missing"


def scan_all(manual_map: dict | None = None) -> dict:
    """
    Escaneia os 66 slots. Retorna:
      { key: {"path": str|None, "source": 'auto'|'manual'|'missing'} }
    """
    manual_map = manual_map or {}
    out: dict = {}
    for cond in CONDITIONS:
        for period in PERIODS:
            key = f"{cond}_{period}"
            path, source = resolve_image(key, manual_map.get(key, ""))
            out[key] = {"path": path or "", "source": source}
    return out


def ensure_skeleton() -> list[str]:
    """
    Cria pastas images/<condition>/ vazias na primeira base GRAVÁVEL
    (pasta do .exe, ou %APPDATA% se ela for somente-leitura).
    Pastas vazias nunca sombreiam fotos do bundle — só dão ao usuário
    o lugar visível onde copiar as fotos.
    """
    target = ""
    for base in _search_bases():
        try:
            os.makedirs(base, exist_ok=True)
            probe = os.path.join(base, ".ww_write_test")
            with open(probe, "w") as f:
                f.write("ok")
            os.remove(probe)
            target = base
            break
        except Exception:
            continue
    if not target:
        return []
    created: list[str] = []
    for cond in CONDITIONS:
        d = os.path.join(target, "images", cond)
        if not os.path.isdir(d):
            os.makedirs(d, exist_ok=True)
            created.append(d)
    if created:
        logger.info(f"[ImageStore] pastas criadas em {target}: {len(created)}")
    return created


def coverage_report(manual_map: dict | None = None) -> dict:
    """Resumo: total/auto/manual/missing + lista de faltantes."""
    data = scan_all(manual_map)
    missing = [k for k, v in data.items() if v["source"] == "missing"]
    auto = [k for k, v in data.items() if v["source"] == "auto"]
    manual = [k for k, v in data.items() if v["source"] == "manual"]
    return {
        "total": len(data),
        "auto": len(auto),
        "manual": len(manual),
        "missing": len(missing),
        "missing_keys": missing,
    }
