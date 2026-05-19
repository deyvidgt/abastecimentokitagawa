# =================================================================
# PAGES/PG_IMPORT_LOG.PY
# =================================================================
import streamlit as st
import db
from theme_web import get_theme


def render():
    t = get_theme(st.session_state.get("tema", "Dark Emerald"))

    st.markdown(f"""
    <h2 style="color:{t['C_TEXT']}">🗂️ Log de Importações</h2>
    <p style="color:{t['C_MUTED']}">Histórico detalhado de arquivos processados</p>
    <hr style="border-color:{t['C_BORDER']};"/>
    """, unsafe_allow_html=True)

    df = db.get_import_log()
    if df.empty:
        st.info("Nenhuma importação registrada ainda.")
        return

    for _, row in df.iterrows():
        data_str = str(row.get("data_import",""))[:16]
        with st.expander(
                f"📂 {row['arquivo']}  —  {data_str}  "
                f"| ✅ {row.get('inseridos',0)}  "
                f"🔁 {row.get('duplicados',0)}  "
                f"❌ {row.get('erros',0)}"):
            c1, c2, c3 = st.columns(3)
            c1.metric("✅ Inseridos",  row.get("inseridos",  0))
            c2.metric("🔁 Duplicados", row.get("duplicados", 0))
            c3.metric("❌ Erros",      row.get("erros",      0))
            if row.get("detalhes"):
                st.code(row["detalhes"], language=None)
