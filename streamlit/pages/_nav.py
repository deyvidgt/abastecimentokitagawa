# =================================================================
# PAGES/_NAV.PY — Sidebar e roteador central
# =================================================================
import streamlit as st


MENU = {
    "📊  Dashboard":            "dashboard",
    "🚛  Gestão de Frota":      "frota",
    "💸  Centro de Custos":     "custos",
    "➕  Novo Registro":        "novo_registro",
    "📋  Registros":            "registros",
    "🚗  Veículos":             "veiculos",
    "👤  Condutores":           "condutores",
    "📥  Importar Planilhas":   "importacao",
    "🗂️  Log de Importações":   "import_log",
    "⚙️  Configurações":        "configuracoes",
}


def render_sidebar():
    with st.sidebar:
        try:
            st.image("logo.png", width=110)
        except Exception:
            st.markdown("## 🚛")

        st.markdown("### KITAGAWA")
        st.markdown("*Enterprise v11 · Web*")
        st.divider()

        # Navegação
        if "pagina" not in st.session_state:
            st.session_state.pagina = "dashboard"

        st.markdown("**ANALÍTICOS**")
        for label in list(MENU.keys())[:5]:
            if st.button(label, use_container_width=True,
                         key=f"nav_{MENU[label]}"):
                st.session_state.pagina = MENU[label]

        st.markdown("**CADASTROS**")
        for label in list(MENU.keys())[5:7]:
            if st.button(label, use_container_width=True,
                         key=f"nav_{MENU[label]}"):
                st.session_state.pagina = MENU[label]

        st.markdown("**SISTEMA**")
        for label in list(MENU.keys())[7:]:
            if st.button(label, use_container_width=True,
                         key=f"nav_{MENU[label]}"):
                st.session_state.pagina = MENU[label]

        st.divider()
        u = st.session_state.usuario
        st.markdown(f"👤 **{u.get('usuario','?')}** · {u.get('perfil','?')}")
        if st.button("🚪  Sair", use_container_width=True):
            st.session_state.logado  = False
            st.session_state.usuario = {}
            st.rerun()


def render_page():
    pagina = st.session_state.get("pagina", "dashboard")

    if pagina == "dashboard":
        from pages import pg_dashboard;      pg_dashboard.render()
    elif pagina == "frota":
        from pages import pg_frota;          pg_frota.render()
    elif pagina == "custos":
        from pages import pg_custos;         pg_custos.render()
    elif pagina == "novo_registro":
        from pages import pg_novo_registro;  pg_novo_registro.render()
    elif pagina == "registros":
        from pages import pg_registros;      pg_registros.render()
    elif pagina == "veiculos":
        from pages import pg_veiculos;       pg_veiculos.render()
    elif pagina == "condutores":
        from pages import pg_condutores;     pg_condutores.render()
    elif pagina == "importacao":
        from pages import pg_importacao;     pg_importacao.render()
    elif pagina == "import_log":
        from pages import pg_import_log;     pg_import_log.render()
    elif pagina == "configuracoes":
        from pages import pg_configuracoes;  pg_configuracoes.render()
