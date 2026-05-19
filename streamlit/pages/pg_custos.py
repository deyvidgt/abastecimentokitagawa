# =================================================================
# PAGES/PG_CUSTOS.PY
# =================================================================
import streamlit as st
import db


def render():
    st.title("💸 Centro de Custos")
    st.caption("Manutenção e despesas por veículo")

    df = db.get_todos_registros()
    if df.empty:
        st.info("Nenhum registro encontrado.")
        return

    # KPIs por categoria
    cats = df.groupby("categoria")["valor"].agg(["sum","count"]).reset_index()
    cols = st.columns(len(cats))
    for i, (_, row) in enumerate(cats.iterrows()):
        cols[i].metric(row["categoria"],
                       f"R$ {row['sum']:,.2f}",
                       f"{int(row['count'])} registros")

    st.divider()

    # Tabela completa
    df_show = df[["data","produto","placa","categoria","valor","responsavel"]].copy()
    df_show["data"]  = df_show["data"].astype(str)
    df_show["valor"] = df_show["valor"].map(lambda x: f"R$ {x:.2f}")
    df_show.columns  = ["Data","Produto","Placa","Categoria","Valor","Responsável"]

    # Filtro rápido
    cat_filter = st.selectbox("Filtrar categoria",
                               ["Todas"] + df["categoria"].dropna().unique().tolist())
    if cat_filter != "Todas":
        df_show = df_show[df_show["Categoria"] == cat_filter]

    st.dataframe(df_show, use_container_width=True, hide_index=True)
