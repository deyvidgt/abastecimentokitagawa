# =================================================================
# THEME_WEB.PY — Temas visuais com CSS responsivo para mobile
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
    usuario = st.session_state.get("usuario", {})
    prefs   = st.session_state.get("preferencias_usuario", {})
    uid     = usuario.get("usuario", "default")
    return prefs.get(uid, {}).get("tema", DEFAULT_THEME)


def salvar_tema_usuario(tema: str):
    usuario = st.session_state.get("usuario", {})
    uid     = usuario.get("usuario", "default")
    if "preferencias_usuario" not in st.session_state:
        st.session_state["preferencias_usuario"] = {}
    if uid not in st.session_state["preferencias_usuario"]:
        st.session_state["preferencias_usuario"][uid] = {}
    st.session_state["preferencias_usuario"][uid]["tema"] = tema
    st.session_state["tema"] = tema
    try:
        import db as db_module
        db_module.salvar_preferencia_usuario(uid, "tema", tema)
    except Exception:
        pass


def carregar_preferencias_usuario():
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

    c_surface = t["C_SURFACE"]
    c_border  = t["C_BORDER"]
    c_text    = t["C_TEXT"]
    c_accent  = t["C_ACCENT"]
    c_muted   = t["C_MUTED"]
    c_bg      = t["C_BG"]

    st.markdown(f"""
<style>
/* ── Reset ── */
[data-testid="stSidebarNav"] {{ display: none !important; }}

/* ── Mobile: padding reduzido ── */
.block-container {{
    padding-top: 0.5rem !important;
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
}}
@media (min-width: 768px) {{
    .block-container {{
        padding-top: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }}
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background-color: {c_surface} !important;
    border-right: 1px solid {c_border};
}}
[data-testid="stSidebar"] * {{ color: {c_text} !important; }}
[data-testid="stSidebar"] .stButton button {{
    background: transparent !important;
    border: none !important;
    text-align: left !important;
    color: {c_text} !important;
    font-size: 13px !important;
    padding: 10px 12px !important;
    border-radius: 8px !important;
    width: 100% !important;
    min-height: 44px !important;
}}
[data-testid="stSidebar"] .stButton button:hover {{
    background: {c_border} !important;
}}

/* ── KPI cards — empilham no mobile ── */
div[data-testid="metric-container"] {{
    background: {c_surface};
    border: 1px solid {c_border};
    border-radius: 12px;
    padding: 12px;
    min-width: 0;
}}

/* ── Tabelas scroll horizontal no mobile ── */
.stDataFrame {{
    border-radius: 10px;
    overflow-x: auto !important;
}}
.stDataFrame > div {{
    overflow-x: auto !important;
}}

/* ── Inputs maiores no mobile (fácil de tocar) ── */
@media (max-width: 768px) {{
    input, select, textarea {{
        font-size: 16px !important;
        min-height: 44px !important;
    }}
    .stSelectbox > div > div {{
        min-height: 44px !important;
    }}
    .stNumberInput input {{
        min-height: 44px !important;
    }}
    /* Botões maiores */
    .stButton button {{
        min-height: 48px !important;
        font-size: 15px !important;
    }}
    /* Gráficos — altura menor no mobile */
    .js-plotly-plot {{
        max-height: 300px !important;
    }}
    /* Colunas empilham no mobile */
    [data-testid="column"] {{
        min-width: 100% !important;
    }}
}}

/* ── Login logo ── */
.login-logo {{
    width: 130px; height: 130px;
    object-fit: contain; border-radius: 50%;
    box-shadow: 0 0 40px {c_accent}80;
    animation: pulse 3s infinite;
    display: block; margin: 0 auto 16px auto;
}}
@media (max-width: 768px) {{
    .login-logo {{ width: 100px; height: 100px; }}
}}
@keyframes pulse {{
    0%   {{ box-shadow: 0 0 20px {c_accent}40; }}
    50%  {{ box-shadow: 0 0 60px {c_accent}cc; }}
    100% {{ box-shadow: 0 0 20px {c_accent}40; }}
}}
.login-title {{
    font-size: 2rem; font-weight: 900;
    color: {c_text}; letter-spacing: 6px;
    text-align: center; margin: 0 0 4px 0;
}}
@media (max-width: 768px) {{
    .login-title {{ font-size: 1.5rem; letter-spacing: 3px; }}
}}
.login-subtitle {{
    color: {c_muted}; font-size: 0.9rem;
    text-align: center; margin-bottom: 28px;
}}
.btn-importar button {{
    background: {c_accent} !important;
    color: white !important;
    font-weight: bold !important;
    border-radius: 10px !important;
    height: 44px !important;
}}
</style>
""", unsafe_allow_html=True)

    # CSS adicional para temas claros
    if t["mode"] == "light":
        st.markdown(f"""
<style>
.main {{ background-color: {c_bg} !important; }}
[data-testid="stAppViewContainer"] {{ background-color: {c_bg} !important; }}
</style>
""", unsafe_allow_html=True)
