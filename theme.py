# =================================================================
# THEME.PY — Definição e persistência de temas visuais
# =================================================================
import json
import os
import sys
import logging

THEME_FILE = "theme.json"

# =================================================================
# Catálogo de temas
# =================================================================
THEMES = {
    "Dark Blue": {
        "label":     "🌑  Dark Blue",
        "C_BG":      "#111318",
        "C_SURFACE": "#1A1D23",
        "C_BORDER":  "#2A2D35",
        "C_ACCENT":  "#3B82F6",
        "C_SUCCESS": "#22C55E",
        "C_WARNING": "#F59E0B",
        "C_DANGER":  "#EF4444",
        "C_TEXT":    "#E2E8F0",
        "C_MUTED":   "#64748B",
        "ctk_mode":  "Dark",
    },
    "Dark Emerald": {
        "label":     "🌿  Dark Emerald",
        "C_BG":      "#0D1612",
        "C_SURFACE": "#14201A",
        "C_BORDER":  "#1F3328",
        "C_ACCENT":  "#10B981",
        "C_SUCCESS": "#34D399",
        "C_WARNING": "#F59E0B",
        "C_DANGER":  "#EF4444",
        "C_TEXT":    "#D1FAE5",
        "C_MUTED":   "#4A7C65",
        "ctk_mode":  "Dark",
    },
    "Dark Purple": {
        "label":     "🔮  Dark Purple",
        "C_BG":      "#0D0D1A",
        "C_SURFACE": "#14142B",
        "C_BORDER":  "#252545",
        "C_ACCENT":  "#8B5CF6",
        "C_SUCCESS": "#22C55E",
        "C_WARNING": "#F59E0B",
        "C_DANGER":  "#EF4444",
        "C_TEXT":    "#EDE9FE",
        "C_MUTED":   "#6D5D8A",
        "ctk_mode":  "Dark",
    },
    "Dark Amber": {
        "label":     "🔥  Dark Amber",
        "C_BG":      "#15100A",
        "C_SURFACE": "#1E1610",
        "C_BORDER":  "#38280E",
        "C_ACCENT":  "#F59E0B",
        "C_SUCCESS": "#22C55E",
        "C_WARNING": "#FB923C",
        "C_DANGER":  "#EF4444",
        "C_TEXT":    "#FEF3C7",
        "C_MUTED":   "#8A6A38",
        "ctk_mode":  "Dark",
    },
    "Light": {
        "label":     "☀️  Light",
        "C_BG":      "#F1F5F9",
        "C_SURFACE": "#FFFFFF",
        "C_BORDER":  "#CBD5E1",
        "C_ACCENT":  "#2563EB",
        "C_SUCCESS": "#16A34A",
        "C_WARNING": "#D97706",
        "C_DANGER":  "#DC2626",
        "C_TEXT":    "#1E293B",
        "C_MUTED":   "#64748B",
        "ctk_mode":  "Light",
    },
}

DEFAULT_THEME = "Dark Blue"

# Nomes de todos os módulos que fazem "from config import C_*"
_COLOR_MODULES = [
    "config",
    "ui.app",
    "ui.widgets",
    "ui.dialogs",
    "ui.views.dashboard",
    "ui.views.frota",
    "ui.views.custos",
    "ui.views.registros",
    "ui.views.cadastros",
    "ui.views.importacao",
    "ui.views.configuracoes",
    "export",
]

_COLOR_KEYS = [
    "C_BG", "C_SURFACE", "C_BORDER", "C_ACCENT",
    "C_SUCCESS", "C_WARNING", "C_DANGER", "C_TEXT", "C_MUTED",
]


# =================================================================
# Leitura / gravação
# =================================================================
def get_saved_theme_name() -> str:
    """Retorna o nome do tema salvo, ou o padrão se não existir."""
    try:
        if os.path.exists(THEME_FILE):
            with open(THEME_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            name = data.get("theme", DEFAULT_THEME)
            return name if name in THEMES else DEFAULT_THEME
    except Exception as e:
        logging.warning(f"theme: não foi possível ler {THEME_FILE}: {e}")
    return DEFAULT_THEME


def get_saved_theme() -> dict:
    """Retorna o dicionário de cores do tema salvo."""
    return THEMES[get_saved_theme_name()]


def save_theme(name: str) -> bool:
    """Persiste o nome do tema escolhido em theme.json."""
    if name not in THEMES:
        logging.error(f"Tema desconhecido: {name}")
        return False
    try:
        with open(THEME_FILE, "w", encoding="utf-8") as f:
            json.dump({"theme": name}, f, indent=2)
        return True
    except Exception as e:
        logging.error(f"theme: não foi possível salvar {THEME_FILE}: {e}")
        return False


# =================================================================
# Aplicação em runtime SEM reiniciar
# =================================================================
def apply_theme_live(app, name: str) -> bool:
    """
    Troca o tema sem reiniciar o processo:

    1. Salva o nome em theme.json
    2. Propaga as novas cores para todos os módulos que fizeram
       "from config import C_*" (atualiza a variável no namespace
       de cada módulo já carregado em sys.modules)
    3. Atualiza o modo do CustomTkinter
    4. Agenda a reconstrução da UI na thread principal via after()
    """
    if name not in THEMES:
        logging.error(f"Tema desconhecido: {name}")
        return False

    if not save_theme(name):
        return False

    t = THEMES[name]

    # ── 1. Atualiza config (fonte canônica) ───────────────────────
    import config
    for k in _COLOR_KEYS:
        setattr(config, k, t[k])
    config.CURRENT_THEME_NAME = name
    config.apply_matplotlib_theme()

    # ── 2. Propaga para todos os módulos já importados ────────────
    # Quando Python faz "from config import C_BG", cria uma variável
    # LOCAL no módulo destino. Atualizar sys.modules[mod].C_BG
    # atualiza exatamente essa variável local.
    for mod_name in _COLOR_MODULES:
        mod = sys.modules.get(mod_name)
        if mod is None:
            continue
        for k in _COLOR_KEYS:
            if hasattr(mod, k):
                setattr(mod, k, t[k])

    # ── 3. Atualiza CustomTkinter ─────────────────────────────────
    import customtkinter as ctk
    ctk.set_appearance_mode(t.get("ctk_mode", "Dark"))

    # ── 4. Reconstrói a UI na thread principal ────────────────────
    # Usa after() para não destruir widgets enquanto ainda estamos
    # dentro do callback do botão que os contém.
    app.after(50, app._rebuild_ui)
    return True


# =================================================================
# Mantido por compatibilidade — não é mais chamado internamente
# =================================================================
def restart_app():
    """
    Reinicia o processo (fallback; prefer apply_theme_live).
    """
    try:
        if getattr(sys, "frozen", False):
            os.execv(sys.executable, [sys.executable] + sys.argv[1:])
        else:
            os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        logging.error(f"restart_app: {e}")
