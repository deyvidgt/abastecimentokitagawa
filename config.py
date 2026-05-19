# =================================================================
# CONFIG.PY — Constantes globais, cores e configuração visual
# =================================================================
import logging
import matplotlib.pyplot as plt
import customtkinter as ctk

# ── Carregar tema ANTES de definir qualquer cor ───────────────────
# theme.py é importado aqui para que todas as views que fazem
# "from config import C_BG" já recebam a cor do tema salvo.
from theme import get_saved_theme, get_saved_theme_name
_T = get_saved_theme()

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

DB_NAME      = "abastecimento_erp_v11.db"
CAMINHO_LOGO = "logo.png"

# ── Paleta de cores (populada pelo tema ativo) ────────────────────
C_BG      = _T["C_BG"]
C_SURFACE = _T["C_SURFACE"]
C_BORDER  = _T["C_BORDER"]
C_ACCENT  = _T["C_ACCENT"]
C_SUCCESS = _T["C_SUCCESS"]
C_WARNING = _T["C_WARNING"]
C_DANGER  = _T["C_DANGER"]
C_TEXT    = _T["C_TEXT"]
C_MUTED   = _T["C_MUTED"]

CURRENT_THEME_NAME = get_saved_theme_name()

# ── Matplotlib defaults ───────────────────────────────────────────
def apply_matplotlib_theme():
    plt.rcParams.update({
        "figure.facecolor":  C_BG,
        "axes.facecolor":    C_SURFACE,
        "axes.edgecolor":    C_BORDER,
        "axes.labelcolor":   C_TEXT,
        "xtick.color":       C_MUTED,
        "ytick.color":       C_MUTED,
        "text.color":        C_TEXT,
        "grid.color":        C_BORDER,
        "grid.linestyle":    "--",
        "grid.alpha":        0.5,
        "font.family":       "DejaVu Sans",
        "axes.spines.top":   False,
        "axes.spines.right": False,
    })

apply_matplotlib_theme()

# ── CustomTkinter theme ───────────────────────────────────────────
ctk.set_appearance_mode(_T.get("ctk_mode", "Dark"))
ctk.set_default_color_theme("blue")
