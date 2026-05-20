# =================================================================
# PAGES/PG_CUSTOS.PY
# =================================================================
import streamlit as st
import pandas as pd
from datetime import datetime
import db
from theme_web import get_theme
from export_utils import botoes_download


def render():
    t = get_theme(st.session_state.get("tema", "Dark Emerald"))

    st.markdown(f"""
    <h2 style="color:{t['C_TEXT']}">💸 Centro de Custos</h2>
    <p style="color:{t['C_MUTED']}">Manutenção e despesas por veículo</p>
    <hr style="border-color:{t['C_BORDER']};"/>
    """, unsafe_allow_html=True)

    df = db.get_todos_registros()
    if df.empty:
        st.info("Nenhum registro encontrado."); return

    # ── KPIs ─────────────────────────────────────────────────────
    cats = df.groupby("categoria")["valor"].agg(["sum","count"]).reset_index()
    cols = st.columns(max(len(cats),1))
    for i,(_,row) in enumerate(cats.iterrows()):
        cols[i].metric(row["categoria"],
                       f"R$ {row['sum']:,.2f}",
                       f"{int(row['count'])} registros")

    # ── Downloads ─────────────────────────────────────────────────
    resumo_cat = df.groupby("categoria").agg(
        total=("valor","sum"),registros=("valor","count"),
        media=("valor","mean")).reset_index()
    resumo_cat.columns = ["Categoria","Total R$","Registros","Média R$"]

    por_placa = df.groupby(["placa","categoria"])["valor"].sum().unstack(
        fill_value=0).reset_index()

    det = df[["data","produto","placa","categoria","valor","quantidade","responsavel"]].copy()
    det["data"] = det["data"].astype(str)
    det.columns = ["Data","Produto","Placa","Categoria","Valor R$","Litros","Responsável"]

    df2 = df.copy()
    df2["mes"] = pd.to_datetime(df2["data"],errors="coerce").dt.to_period("M").astype(str)
    mensal = df2.groupby(["mes","categoria"])["valor"].sum().unstack(
        fill_value=0).reset_index()

    botoes_download(st, resumo_cat, "custos",
        "CENTRO DE CUSTOS — KITAGAWA",
        colunas_pdf=["Categoria","Total R$","Registros","Média R$"],
        sheets_excel={
            "Resumo":      resumo_cat,
            "Por Veículo": por_placa,
            "Detalhes":    det,
            "Mensal":      mensal,
        })

    st.divider()

    # ── Filtros e tabela ──────────────────────────────────────────
    c1,c2 = st.columns([2,4])
    cat_f   = c1.selectbox("Filtrar categoria",
                            ["Todas"]+df["categoria"].dropna().unique().tolist())
    placa_f = c2.text_input("Filtrar placa", placeholder="ex: ABC1234")

    df_show = det.copy()
    if cat_f != "Todas":
        df_show = df_show[df_show["Categoria"]==cat_f]
    if placa_f:
        df_show = df_show[df_show["Placa"].str.contains(placa_f.upper(),na=False)]

    st.dataframe(df_show, use_container_width=True, hide_index=True)
