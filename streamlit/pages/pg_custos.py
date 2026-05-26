# =================================================================
# PAGES/PG_CUSTOS.PY
# =================================================================
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
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

    c1,c2,c3,c4,c5,c6 = st.columns([1.4,1.4,.6,.6,.6,.8])
    with c1: data_ini = st.date_input("De",  value=datetime(2000,1,1).date(), key="cust_ini")
    with c2: data_fim = st.date_input("Até", value=datetime.now().date(),     key="cust_fim")
    with c3:
        if st.button("30d",  key="c30"):  data_ini=(datetime.now()-timedelta(30)).date();  data_fim=datetime.now().date()
    with c4:
        if st.button("90d",  key="c90"):  data_ini=(datetime.now()-timedelta(90)).date();  data_fim=datetime.now().date()
    with c5:
        if st.button("1ano", key="c1a"):  data_ini=(datetime.now()-timedelta(365)).date(); data_fim=datetime.now().date()
    with c6:
        if st.button("Tudo", key="ctudo"): data_ini=datetime(2000,1,1).date(); data_fim=datetime.now().date()

    df = db.get_registros(data_ini=str(data_ini), data_fim=str(data_fim), limit=10000)
    df = df.dropna(subset=["data"]) if not df.empty else df

    if df.empty:
        st.warning("Nenhum registro no período selecionado."); return

    st.caption(f"📅 {data_ini.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')} · {len(df)} registros")

    # ── KPIs ─────────────────────────────────────────────────────
    cats = df.groupby("categoria")["valor"].agg(["sum","count"]).reset_index()
    cols = st.columns(max(len(cats),1))
    for i,(_,row) in enumerate(cats.iterrows()):
        cols[i].metric(row["categoria"], f"R$ {row['sum']:,.2f}", f"{int(row['count'])} registros")

    # ── Downloads ─────────────────────────────────────────────────
    resumo_cat = df.groupby("categoria").agg(
        total=("valor","sum"),registros=("valor","count"),
        media=("valor","mean")).reset_index()
    resumo_cat.columns = ["Categoria","Total R$","Registros","Média R$"]

    por_placa = df.groupby(["placa","categoria"])["valor"].sum().unstack(fill_value=0).reset_index()

    det = df[["data_fmt","produto","placa","categoria","valor","quantidade","responsavel"]].copy()
    det.columns = ["Data","Produto","Placa","Categoria","Valor R$","Litros","Responsável"]

    df2 = df.copy()
    df2["mes"] = df2["data"].dt.to_period("M").astype(str)
    mensal = df2.groupby(["mes","categoria"])["valor"].sum().unstack(fill_value=0).reset_index()

    botoes_download(st, resumo_cat, "custos",
        f"CENTRO DE CUSTOS — {data_ini.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}",
        colunas_pdf=["Categoria","Total R$","Registros","Média R$"],
        sheets_excel={"Resumo":resumo_cat,"Por Veículo":por_placa,"Detalhes":det,"Mensal":mensal})

    st.divider()

    c1,c2 = st.columns([2,4])
    cat_f   = c1.selectbox("Categoria", ["Todas"]+df["categoria"].dropna().unique().tolist())
    placa_f = c2.text_input("Placa", placeholder="ex: ABC1234")

    df_show = det.copy()
    if cat_f != "Todas":
        df_show = df_show[df_show["Categoria"]==cat_f]
    if placa_f:
        df_show = df_show[df_show["Placa"].str.contains(placa_f.upper(),na=False)]

    st.dataframe(df_show, use_container_width=True, hide_index=True)
