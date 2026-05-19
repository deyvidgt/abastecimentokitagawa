# =================================================================
# PAGES/_NAV.PY — Sidebar e roteador central
# =================================================================
import streamlit as st
import base64
import os
from theme_web import get_theme


def _get_logo_b64():
    for path in ["streamlit/logo.png", "logo.png"]:
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return ""


def render_sidebar():
    t = get_theme(st.session_state.get("tema", "Dark Emerald"))

    with st.sidebar:
        # Logo
        logo_b64 = _get_logo_b64()
        if logo_b64:
            st.markdown(f"""
            <div style="text-align:center;padding:24px 0 8px 0;">
                <img src="data:image/png;base64,{logo_b64}"
                     style="width:110px;height:110px;object-fit:contain;
                            border-radius:50%;
                            box-shadow:0 0 24px {t['C_ACCENT']}80;"/>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="text-align:center;margin-bottom:4px;">
            <span style="font-size:16px;font-weight:900;
                         color:{t['C_TEXT']};letter-spacing:2px;">
                ABASTECIMENTOS
            </span><br>
            <span style="font-size:10px;color:{t['C_MUTED']};">
                Enterprise v11.0 · Web
            </span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"<hr style='border-color:{t['C_BORDER']};margin:8px 0;'/>",
                    unsafe_allow_html=True)

        if "pagina" not in st.session_state:
            st.session_state.pagina = "dashboard"

        def nav_group(label):
            st.markdown(f"""
            <p style="font-size:10px;font-weight:700;
                      color:{t['C_MUTED']};margin:16px 0 4px 8px;
                      letter-spacing:1px;">{label}</p>
            """, unsafe_allow_html=True)

        def nav_btn(label, pagina):
            ativo = st.session_state.pagina == pagina
            bg    = t['C_ACCENT'] if ativo else "transparent"
            cor   = "white"       if ativo else t['C_TEXT']
            if st.button(label, key=f"nav_{pagina}", use_container_width=True):
                st.session_state.pagina = pagina
                st.rerun()

        nav_group("ANALÍTICOS")
        nav_btn("📊  Dashboard",          "dashboard")
        nav_btn("🚛  Gestão de Frota",    "frota")
        nav_btn("💸  Centro de Custos",   "custos")
        nav_btn("➕  Novo Registro",      "novo_registro")
        nav_btn("📋  Registros",          "registros")

        nav_group("CADASTROS")
        nav_btn("🚗  Veículos",           "veiculos")
        nav_btn("👤  Condutores",          "condutores")

        nav_group("SISTEMA")
        nav_btn("🗂️  Log de Importações", "import_log")
        nav_btn("⚙️  Configurações",      "configuracoes")

        st.markdown(f"<hr style='border-color:{t['C_BORDER']};margin:8px 0;'/>",
                    unsafe_allow_html=True)

        # Botão importar lote
        st.markdown('<div class="btn-importar">', unsafe_allow_html=True)
        if st.button("📥  IMPORTAR LOTE", use_container_width=True,
                     key="btn_importar_sidebar"):
            st.session_state.pagina = "importacao"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Status DB
        st.markdown(f"""
        <p style="font-size:11px;color:{t['C_SUCCESS']};
                  margin:8px 0 4px 8px;">● DB Conectado</p>
        """, unsafe_allow_html=True)

        # Usuário logado + sair
        u = st.session_state.get("usuario", {})
        st.markdown(f"""
        <p style="font-size:11px;color:{t['C_MUTED']};margin:0 0 8px 8px;">
            👤 {u.get('usuario','?')} · {u.get('perfil','?')}
        </p>
        """, unsafe_allow_html=True)

        if st.button("🚪  Sair", use_container_width=True, key="btn_sair"):
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
