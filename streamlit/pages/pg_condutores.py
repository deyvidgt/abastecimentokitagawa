# =================================================================
# PAGES/PG_CONDUTORES.PY
# =================================================================
import streamlit as st
from datetime import datetime
import db
from theme_web import get_theme


def render():
    t = get_theme(st.session_state.get("tema", "Dark Emerald"))

    st.markdown(f"""
    <h2 style="color:{t['C_TEXT']}">👤 Cadastro de Condutores</h2>
    <hr style="border-color:{t['C_BORDER']};"/>
    """, unsafe_allow_html=True)

    with st.expander("➕ Novo condutor", expanded=True):
        c1, c2 = st.columns([3, 1])
        nome = c1.text_input("Nome completo", placeholder="ex: JOÃO SILVA")
        with c2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Adicionar", type="primary",
                          use_container_width=True, key="add_cond"):
                n = nome.upper().strip()
                if not n:
                    st.warning("Informe o nome.")
                elif db.inserir_condutor(n):
                    st.success(f"✅ {n} cadastrado!")
                    st.rerun()
                else:
                    st.error("Condutor já existe.")

    st.divider()
    df = db.get_condutores()
    if df.empty:
        st.info("Nenhum condutor cadastrado.")
    else:
        st.dataframe(df[["nome"]] if "nome" in df.columns else df,
                     use_container_width=True, hide_index=True)
