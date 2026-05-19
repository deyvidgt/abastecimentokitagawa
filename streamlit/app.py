# =================================================================
# APP.PY — Ponto de entrada do sistema Streamlit
# =================================================================
import streamlit as st
import base64
import os

st.set_page_config(
    page_title="KITAGAWA — Gestão de Abastecimento",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stSidebar"] { background-color: #1A1D23; }
[data-testid="stSidebar"] * { color: #E2E8F0 !important; }
.block-container { padding-top: 1.5rem; }
div[data-testid="metric-container"] {
    background: #1A1D23;
    border: 1px solid #2A2D35;
    border-radius: 12px;
    padding: 16px;
}
.login-logo {
    width: 160px;
    height: 160px;
    object-fit: contain;
    border-radius: 50%;
    box-shadow: 0 0 40px rgba(16,185,129,0.5);
    animation: pulse 3s infinite;
    display: block;
    margin: 0 auto 16px auto;
}
@keyframes pulse {
    0%   { box-shadow: 0 0 20px rgba(16,185,129,0.3); }
    50%  { box-shadow: 0 0 60px rgba(16,185,129,0.8); }
    100% { box-shadow: 0 0 20px rgba(16,185,129,0.3); }
}
.login-title {
    font-size: 2.2rem;
    font-weight: 900;
    color: #D1FAE5;
    letter-spacing: 6px;
    text-align: center;
    margin: 0 0 4px 0;
}
.login-subtitle {
    color: #4A7C65;
    font-size: 0.9rem;
    text-align: center;
    margin-bottom: 28px;
}
.login-card {
    background: #14201A;
    border: 1px solid #1F3328;
    border-radius: 18px;
    padding: 32px 36px;
    box-shadow: 0 12px 48px rgba(0,0,0,0.5);
}
</style>
""", unsafe_allow_html=True)

import db

if "logado" not in st.session_state:
    st.session_state.logado  = False
    st.session_state.usuario = {}

# =================================================================
# TELA DE LOGIN
# =================================================================
if not st.session_state.logado:

    # Carrega logo como base64
    logo_b64 = ""
    for path in ["logo.png", "streamlit/logo.png", "../logo.png"]:
        if os.path.exists(path):
            with open(path, "rb") as f:
                logo_b64 = base64.b64encode(f.read()).decode()
            break

    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])

    with col:
        # Logo centralizado
        if logo_b64:
            st.markdown(f"""
            <img src="data:image/png;base64,{logo_b64}" class="login-logo"/>
            """, unsafe_allow_html=True)
        else:
            st.markdown(
                '<div style="text-align:center;font-size:90px;">🚛</div>',
                unsafe_allow_html=True)

        # Título
        st.markdown("""
        <p class="login-title">KITAGAWA</p>
        <p class="login-subtitle">Sistema de Gestão de Abastecimento</p>
        """, unsafe_allow_html=True)

        # Card login
        st.markdown('<div class="login-card">', unsafe_allow_html=True)

        with st.form("form_login"):
            usuario = st.text_input("👤  Usuário")
            senha   = st.text_input("🔒  Senha", type="password")
            entrar  = st.form_submit_button(
                "▶  ENTRAR",
                use_container_width=True,
                type="primary")

        st.markdown("</div>", unsafe_allow_html=True)

        if entrar:
            if not usuario or not senha:
                st.warning("Preencha usuário e senha.")
            else:
                u = db.verificar_login(usuario, senha)
                if u:
                    st.session_state.logado  = True
                    st.session_state.usuario = u
                    st.rerun()
                else:
                    st.error("❌  Usuário ou senha incorretos.")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🔑  Esqueci / alterar senha",
                     use_container_width=True):
            st.session_state["mostrar_alterar_senha"] = (
                not st.session_state.get("mostrar_alterar_senha", False))

        if st.session_state.get("mostrar_alterar_senha"):
            st.divider()
            st.markdown("#### Alterar senha")
            with st.form("form_alterar"):
                u2   = st.text_input("Usuário")
                ant  = st.text_input("Senha atual (admin deixa em branco)",
                                      type="password")
                nov  = st.text_input("Nova senha", type="password")
                conf = st.text_input("Confirmar nova senha", type="password")
                salvar = st.form_submit_button("💾  Salvar",
                                               use_container_width=True,
                                               type="primary")
            if salvar:
                if len(nov) < 6:
                    st.warning("Mínimo 6 caracteres.")
                elif nov != conf:
                    st.error("As senhas não coincidem.")
                elif ant and not db.verificar_login(u2, ant):
                    st.error("Senha atual incorreta.")
                elif db.alterar_senha(u2, nov):
                    st.success(f"✅ Senha de '{u2}' alterada!")
                    st.session_state["mostrar_alterar_senha"] = False
                else:
                    st.error(f"Usuário '{u2}' não encontrado.")

    st.stop()

# =================================================================
# APLICAÇÃO PRINCIPAL
# =================================================================
from pages._nav import render_sidebar, render_page
render_sidebar()
render_page()
