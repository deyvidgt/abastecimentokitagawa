# =================================================================
# PAGES/PG_CONDUTORES.PY
# =================================================================
import streamlit as st
import db


def render():
    st.title("👤 Cadastro de Condutores")

    with st.expander("➕ Novo condutor", expanded=True):
        nome = st.text_input("Nome completo")
        if st.button("➕ Adicionar", type="primary"):
            if not nome:
                st.warning("Informe o nome.")
            elif db.inserir_condutor(nome):
                st.success(f"{nome.upper()} cadastrado!")
                st.rerun()
            else:
                st.error("Condutor já existe.")

    st.divider()
    df = db.get_condutores()
    if df.empty:
        st.info("Nenhum condutor cadastrado.")
    else:
        st.dataframe(df[["nome"]], use_container_width=True, hide_index=True)
