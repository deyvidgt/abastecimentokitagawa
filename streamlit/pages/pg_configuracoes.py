# =================================================================
# PAGES/PG_CONFIGURACOES.PY — Tema por usuário + Usuários
# =================================================================
import streamlit as st
import db
from theme_web import (THEMES, get_theme, get_tema_usuario,
                        salvar_tema_usuario, DEFAULT_THEME)


def render():
    t = get_theme(st.session_state.get("tema", DEFAULT_THEME))
    usuario_logado = st.session_state.get("usuario", {}).get("usuario", "?")

    st.markdown(f"""
    <h2 style="color:{t['C_TEXT']}">⚙️ Configurações</h2>
    <p style="color:{t['C_MUTED']}">Personalize sua experiência</p>
    <hr style="border-color:{t['C_BORDER']};"/>
    """, unsafe_allow_html=True)

    # ── Tema por usuário ──────────────────────────────────────────
    st.markdown(f"### 🎨 Tema Visual")
    st.caption(f"Sua preferência é salva individualmente para **{usuario_logado}**.")

    tema_atual = get_tema_usuario()

    # Separar temas escuros e claros
    temas_escuros = {k: v for k, v in THEMES.items() if v["mode"] == "dark"}
    temas_claros  = {k: v for k, v in THEMES.items() if v["mode"] == "light"}

    st.markdown(f"**🌑 Temas Escuros**")
    cols = st.columns(len(temas_escuros))
    for i, (nome, td) in enumerate(temas_escuros.items()):
        with cols[i]:
            ativo = nome == tema_atual
            borda = f"3px solid {td['C_ACCENT']}" if ativo else f"1px solid {td['C_BORDER']}"
            st.markdown(f"""
            <div style="background:{td['C_SURFACE']};border:{borda};
                        border-radius:12px;padding:12px;text-align:center;
                        margin-bottom:8px;">
                <div style="display:flex;justify-content:center;gap:4px;margin-bottom:8px;">
                    <div style="width:16px;height:16px;border-radius:50%;background:{td['C_ACCENT']};"></div>
                    <div style="width:16px;height:16px;border-radius:50%;background:{td['C_SUCCESS']};"></div>
                    <div style="width:16px;height:16px;border-radius:50%;background:{td['C_WARNING']};"></div>
                    <div style="width:16px;height:16px;border-radius:50%;background:{td['C_DANGER']};"></div>
                </div>
                <p style="color:{td['C_TEXT']};font-weight:700;font-size:12px;margin:0;">{td['label']}</p>
                <p style="color:{td['C_ACCENT']};font-size:10px;margin:2px 0 0 0;">
                    {"✔ Ativo" if ativo else "&nbsp;"}
                </p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Aplicar", key=f"tema_{nome}",
                         use_container_width=True,
                         type="primary" if ativo else "secondary"):
                salvar_tema_usuario(nome)
                st.success(f"Tema '{nome}' aplicado!")
                st.rerun()

    st.markdown(f"**☀️ Temas Claros**")
    cols2 = st.columns(len(temas_claros))
    for i, (nome, td) in enumerate(temas_claros.items()):
        with cols2[i]:
            ativo = nome == tema_atual
            borda = f"3px solid {td['C_ACCENT']}" if ativo else f"1px solid {td['C_BORDER']}"
            st.markdown(f"""
            <div style="background:{td['C_SURFACE']};border:{borda};
                        border-radius:12px;padding:12px;text-align:center;
                        margin-bottom:8px;">
                <div style="display:flex;justify-content:center;gap:4px;margin-bottom:8px;">
                    <div style="width:16px;height:16px;border-radius:50%;background:{td['C_ACCENT']};"></div>
                    <div style="width:16px;height:16px;border-radius:50%;background:{td['C_SUCCESS']};"></div>
                    <div style="width:16px;height:16px;border-radius:50%;background:{td['C_WARNING']};"></div>
                    <div style="width:16px;height:16px;border-radius:50%;background:{td['C_DANGER']};"></div>
                </div>
                <p style="color:{td['C_TEXT']};font-weight:700;font-size:12px;margin:0;">{td['label']}</p>
                <p style="color:{td['C_ACCENT']};font-size:10px;margin:2px 0 0 0;">
                    {"✔ Ativo" if ativo else "&nbsp;"}
                </p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Aplicar", key=f"tema_{nome}",
                         use_container_width=True,
                         type="primary" if ativo else "secondary"):
                salvar_tema_usuario(nome)
                st.success(f"Tema '{nome}' aplicado!")
                st.rerun()

    st.divider()

    # ── Usuários ──────────────────────────────────────────────────
    st.markdown("### 👥 Usuários do sistema")
    df_u = db.listar_usuarios()
    if not df_u.empty:
        st.dataframe(df_u[["usuario","perfil","ativo","criado_em"]],
                     use_container_width=True, hide_index=True)

    with st.expander("➕ Criar novo usuário"):
        c1, c2, c3 = st.columns(3)
        novo_user  = c1.text_input("Usuário", key="nu")
        nova_senha = c2.text_input("Senha", type="password", key="ns")
        perfil     = c3.selectbox("Perfil", ["operador","admin"], key="np")
        if st.button("Criar", type="primary", key="criar_user"):
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
        u_edit  = c1.text_input("Usuário a alterar", key="ua")
        n_senha = c2.text_input("Nova senha", type="password", key="na")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Salvar senha", type="primary", key="salvar_senha"):
                if len(n_senha) < 6:
                    st.warning("Mínimo 6 caracteres.")
                elif db.alterar_senha(u_edit, n_senha):
                    st.success(f"Senha de '{u_edit}' alterada!")
                else:
                    st.error(f"Usuário '{u_edit}' não encontrado.")
        with col2:
            if st.button("🔄 Resetar para '123456'", key="reset_senha"):
                if db.alterar_senha(u_edit, "123456"):
                    st.success(f"Senha de '{u_edit}' resetada para 123456.")
                else:
                    st.error(f"Usuário '{u_edit}' não encontrado.")

    st.divider()
    st.caption("Sistema Abastecimento ERP v11 · Web Edition · Kitagawa")
