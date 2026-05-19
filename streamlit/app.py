# =================================================================
# APP.PY — Ponto de entrada do sistema Streamlit
# =================================================================
import streamlit as st

st.set_page_config(
    page_title="KITAGAWA — Gestão de Abastecimento",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS global ────────────────────────────────────────────────────
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
.stDataFrame { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

import db

# ── Session state ─────────────────────────────────────────────────
if "logado" not in st.session_state:
    st.session_state.logado  = False
    st.session_state.usuario = {}

# =================================================================
# TELA DE LOGIN
# =================================================================
if not st.session_state.logado:

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)

        try:
            st.image("logo.png", width=120)
        except Exception:
            st.markdown("## 🚛")

        st.markdown("## KITAGAWA")
        st.markdown("*Sistema de Gestão de Abastecimento*")
        st.markdown("---")

        with st.form("form_login", clear_on_submit=False):
            usuario = st.text_input("👤  Usuário")
            senha   = st.text_input("🔒  Senha", type="password")
            entrar  = st.form_submit_button("ENTRAR", use_container_width=True,
                                             type="primary")

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
                    st.error("Usuário ou senha incorretos.")

        st.markdown("---")
        if st.button("🔑  Esqueci / alterar senha", use_container_width=True):
            st.session_state["mostrar_alterar_senha"] = True

        # Formulário de alteração de senha inline
        if st.session_state.get("mostrar_alterar_senha"):
            st.markdown("### Alterar senha")
            with st.form("form_alterar"):
                u2   = st.text_input("Usuário")
                ant  = st.text_input("Senha atual (deixe em branco se admin resetando)",
                                      type="password")
                nov  = st.text_input("Nova senha", type="password")
                conf = st.text_input("Confirmar nova senha", type="password")
                salvar = st.form_submit_button("💾  Salvar", type="primary",
                                                use_container_width=True)

            if salvar:
                if len(nov) < 6:
                    st.warning("Mínimo 6 caracteres.")
                elif nov != conf:
                    st.error("As senhas não coincidem.")
                elif ant and not db.verificar_login(u2, ant):
                    st.error("Senha atual incorreta.")
                elif db.alterar_senha(u2, nov):
                    st.success(f"Senha de '{u2}' alterada com sucesso!")
                    st.session_state["mostrar_alterar_senha"] = False
                else:
                    st.error(f"Usuário '{u2}' não encontrado.")

    st.stop()  # Não renderiza nada mais enquanto não logar

# =================================================================
# APLICAÇÃO PRINCIPAL — usuário autenticado
# =================================================================
from pages._nav import render_sidebar, render_page
render_sidebar()
render_page()
