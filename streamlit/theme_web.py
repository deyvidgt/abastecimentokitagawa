# =================================================================
# THEME_WEB.PY — Temas visuais com preferência por usuário
# =================================================================
import streamlit as st

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
        "mode":      "dark",
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
        "mode":      "dark",
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
        "mode":      "dark",
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
        "mode":      "dark",
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
        "mode":      "light",
    },
    "Light Green": {
        "label":     "🌱  Light Green",
        "C_BG":      "#F0FDF4",
        "C_SURFACE": "#FFFFFF",
        "C_BORDER":  "#BBF7D0",
        "C_ACCENT":  "#16A34A",
        "C_SUCCESS": "#15803D",
        "C_WARNING": "#D97706",
        "C_DANGER":  "#DC2626",
        "C_TEXT":    "#14532D",
        "C_MUTED":   "#4B7A5E",
        "mode":      "light",
    },
}

DEFAULT_THEME = "Dark Emerald"


def get_tema_usuario() -> str:
    """Retorna o tema salvo para o usuário atual."""
    usuario = st.session_state.get("usuario", {})
    prefs   = st.session_state.get("preferencias_usuario", {})
    uid     = usuario.get("usuario", "default")
    return prefs.get(uid, {}).get("tema", DEFAULT_THEME)


def salvar_tema_usuario(tema: str):
    """Salva o tema nas preferências do usuário (session_state)."""
    usuario = st.session_state.get("usuario", {})
    uid     = usuario.get("usuario", "default")
    if "preferencias_usuario" not in st.session_state:
        st.session_state["preferencias_usuario"] = {}
    if uid not in st.session_state["preferencias_usuario"]:
        st.session_state["preferencias_usuario"][uid] = {}
    st.session_state["preferencias_usuario"][uid]["tema"] = tema
    # Também atualiza o tema global da sessão
    st.session_state["tema"] = tema

    # Persiste no Supabase
    try:
        import db as db_module
        db_module.salvar_preferencia_usuario(uid, "tema", tema)
    except Exception:
        pass  # Falha silenciosa — tema continua na sessão


def carregar_preferencias_usuario():
    """Carrega preferências do usuário do Supabase ao fazer login."""
    usuario = st.session_state.get("usuario", {})
    uid     = usuario.get("usuario", "default")
    try:
        import db as db_module
        tema = db_module.get_preferencia_usuario(uid, "tema")
        if tema and tema in THEMES:
            if "preferencias_usuario" not in st.session_state:
                st.session_state["preferencias_usuario"] = {}
            if uid not in st.session_state["preferencias_usuario"]:
                st.session_state["preferencias_usuario"][uid] = {}
            st.session_state["preferencias_usuario"][uid]["tema"] = tema
            st.session_state["tema"] = tema
    except Exception:
        pass


def get_theme(name: str = None) -> dict:
    if name is None:
        name = get_tema_usuario()
    return THEMES.get(name, THEMES[DEFAULT_THEME])


def apply_css(theme_name: str = None):
    t = get_theme(theme_name)
    st.markdown(f"""
<style>
[data-testid="stSidebarNav"] {{ display: none !important; }}
.block-container {{ padding-top: 1rem !important; }}

[data-testid="stSidebar"] {{
    background-color: {t['C_SURFACE']} !important;
    border-right: 1px solid {t['C_BORDER']};
}}
[data-testid="stSidebar"] * {{ color: {t['C_TEXT']} !important; }}
[data-testid="stSidebar"] .stButton button {{
    background: transparent !important;
    border: none !important;
    text-align: left !important;
    color: {t['C_TEXT']} !important;
    font-size: 13px !important;
    padding: 8px 12px !important;
    border-radius: 8px !important;
    width: 100% !important;
}}
[data-testid="stSidebar"] .stButton button:hover {{
    background: {t['C_BORDER']} !important;
}}
div[data-testid="metric-container"] {{
    background: {t['C_SURFACE']};
    border: 1px solid {t['C_BORDER']};
    border-radius: 12px;
    padding: 16px;
}}
.stDataFrame {{ border-radius: 10px; }}
.login-logo {{
    width: 160px; height: 160px;
    object-fit: contain; border-radius: 50%;
    box-shadow: 0 0 40px {t['C_ACCENT']}80;
    animation: pulse 3s infinite;
    display: block; margin: 0 auto 16px auto;
}}
@keyframes pulse {{
    0%   {{ box-shadow: 0 0 20px {t['C_ACCENT']}40; }}
    50%  {{ box-shadow: 0 0 60px {t['C_ACCENT']}cc; }}
    100% {{ box-shadow: 0 0 20px {t['C_ACCENT']}40; }}
}}
.login-title {{
    font-size: 2.2rem; font-weight: 900;
    color: {t['C_TEXT']}; letter-spacing: 6px;
    text-align: center; margin: 0 0 4px 0;
}}
.login-subtitle {{
    color: {t['C_MUTED']}; font-size: 0.9rem;
    text-align: center; margin-bottom: 28px;
}}
.btn-importar button {{
    background: {t['C_ACCENT']} !important;
    color: white !important;
    font-weight: bold !important;
    border-radius: 10px !important;
    height: 44px !important;
}}
/* Tema claro — fundo da página */
{"" if t['mode']=='dark' else f"""
.main {{ background-color: {t['C_BG']} !important; }}
[data-testid="stAppViewContainer"] {{ background-color: {t['C_BG']} !important; }}
"""}
</style>
""", unsafe_allow_html=True)
