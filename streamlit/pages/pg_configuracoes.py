# =================================================================
# PAGES/PG_CONFIGURACOES.PY
# =================================================================
import streamlit as st
import db


def render():
    st.title("⚙️ Configurações")

    # ── Usuários ──────────────────────────────────────────────────
    st.subheader("👥 Usuários do sistema")
    df_u = db.listar_usuarios()
    if not df_u.empty:
        st.dataframe(df_u, use_container_width=True, hide_index=True)

    with st.expander("➕ Criar novo usuário"):
        c1, c2, c3 = st.columns(3)
        novo_user   = c1.text_input("Usuário")
        nova_senha  = c2.text_input("Senha", type="password")
        perfil      = c3.selectbox("Perfil", ["operador","admin"])
        if st.button("Criar usuário", type="primary"):
            if not novo_user or not nova_senha:
                st.warning("Preencha todos os campos.")
            elif len(nova_senha) < 6:
                st.warning("Mínimo 6 caracteres.")
            elif db.criar_usuario(novo_user, nova_senha, perfil):
                st.success(f"Usuário '{novo_user}' criado!")
                st.rerun()
            else:
                st.error("Usuário já existe.")

    with st.expander("🔑 Alterar / resetar senha"):
        c1, c2 = st.columns(2)
        u_edit  = c1.text_input("Usuário a alterar")
        n_senha = c2.text_input("Nova senha", type="password")
        if st.button("💾 Salvar senha", type="primary"):
            if len(n_senha) < 6:
                st.warning("Mínimo 6 caracteres.")
            elif db.alterar_senha(u_edit, n_senha):
                st.success(f"Senha de '{u_edit}' alterada!")
            else:
                st.error(f"Usuário '{u_edit}' não encontrado.")

        if st.button("🔄 Resetar para '123456'", type="secondary"):
            if db.alterar_senha(u_edit, "123456"):
                st.success(f"Senha de '{u_edit}' resetada para 123456.")
            else:
                st.error(f"Usuário '{u_edit}' não encontrado.")

    st.divider()
    st.caption("Sistema Abastecimento ERP v11 · Web Edition · Kitagawa")
