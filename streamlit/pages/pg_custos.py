# =================================================================
# PAGES/PG_CUSTOS.PY
# =================================================================
import streamlit as st
import db
from theme_web import get_theme


def render():
    t = get_theme(st.session_state.get("tema", "Dark Emerald"))

    st.markdown(f"""
    <h2 style="color:{t['C_TEXT']}">💸 Centro de Custos</h2>
    <p style="color:{t['C_MUTED']}">Manutenção e despesas por veículo</p>
    <hr style="border-color:{t['C_BORDER']};"/>
    """, unsafe_allow_html=True)

    df = db.get_todos_registros()
    if df.empty:
        st.info("Nenhum registro encontrado.")
        return

    # KPIs por categoria
    cats = df.groupby("categoria")["valor"].agg(["sum","count"]).reset_index()
    cols = st.columns(max(len(cats), 1))
    for i, (_, row) in enumerate(cats.iterrows()):
        cols[i].metric(row["categoria"],
                       f"R$ {row['sum']:,.2f}",
                       f"{int(row['count'])} registros")

    st.divider()

    # Filtro
    cat_opts = ["Todas"] + df["categoria"].dropna().unique().tolist()
    cat_f = st.selectbox("Filtrar categoria", cat_opts)

    df_show = df[["data","produto","placa","categoria","valor","responsavel"]].copy()
    df_show["data"]  = df_show["data"].astype(str)
    df_show["valor"] = df_show["valor"].map(lambda x: f"R$ {x:.2f}")
    df_show.columns = ["Data","Produto","Placa","Categoria","Valor","Responsável"]

    if cat_f != "Todas":
        df_show = df_show[df_show["Categoria"] == cat_f]

    st.dataframe(df_show, use_container_width=True, hide_index=True)
