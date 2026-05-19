# =================================================================
# PAGES/PG_IMPORT_LOG.PY
# =================================================================
import streamlit as st
import db


def render():
    st.title("🗂️ Log de Importações")

    df = db.get_import_log()
    if df.empty:
        st.info("Nenhuma importação registrada.")
        return

    for _, row in df.iterrows():
        with st.expander(f"📂 {row['arquivo']}  —  {str(row.get('data_import',''))[:16]}"):
            c1, c2, c3 = st.columns(3)
            c1.metric("✅ Inseridos",   row.get("inseridos",  0))
            c2.metric("🔁 Duplicados",  row.get("duplicados", 0))
            c3.metric("❌ Erros",       row.get("erros",      0))
            if row.get("detalhes"):
                st.code(row["detalhes"], language=None)
