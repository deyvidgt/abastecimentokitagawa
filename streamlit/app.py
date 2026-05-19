# =================================================================
# APP.PY — Ponto de entrada com sistema de temas
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

from theme_web import apply_css, get_theme, DEFAULT_THEME

# Aplica CSS do tema atual
tema_atual = st.session_state.get("tema", DEFAULT_THEME)
apply_css(tema_atual)
t = get_theme(tema_atual)

import db

if "logado" not in st.session_state:
    st.session_state.logado  = False
    st.session_state.usuario = {}

# =================================================================
# TELA DE LOGIN
# =================================================================
if not st.session_state.logado:

    logo_b64 = ""
    for path in ["streamlit/logo.png", "logo.png"]:
        if os.path.exists(path):
            with open(path, "rb") as f:
                logo_b64 = base64.b64encode(f.read()).decode()
            break

    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])

    with col:
        if logo_b64:
            st.markdown(
                f'<img src="data:image/png;base64,{logo_b64}" class="login-logo"/>',
                unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div style="text-align:center;font-size:90px;">🚛</div>',
                unsafe_allow_html=True)

        st.markdown(f"""
        <p class="login-title">KITAGAWA</p>
        <p class="login-subtitle">Sistema de Gestão de Abastecimento</p>
        """, unsafe_allow_html=True)

        with st.form("form_login"):
            usuario = st.text_input("👤  Usuário")
            senha   = st.text_input("🔒  Senha", type="password")
            entrar  = st.form_submit_button(
                "▶  ENTRAR", use_container_width=True, type="primary")

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
        if st.button("🔑  Esqueci / alterar senha", use_container_width=True):
            st.session_state["mostrar_alterar_senha"] = (
                not st.session_state.get("mostrar_alterar_senha", False))

        if st.session_state.get("mostrar_alterar_senha"):
            st.divider()
            st.markdown("#### Alterar senha")
            with st.form("form_alterar"):
                u2   = st.text_input("Usuário")
                ant  = st.text_input("Senha atual (admin deixa em branco)", type="password")
                nov  = st.text_input("Nova senha", type="password")
                conf = st.text_input("Confirmar nova senha", type="password")
                salvar = st.form_submit_button("💾  Salvar",
                    use_container_width=True, type="primary")
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
