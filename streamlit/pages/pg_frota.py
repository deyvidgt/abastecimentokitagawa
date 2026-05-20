# =================================================================
# PAGES/PG_FROTA.PY — com filtro de período
# =================================================================
import streamlit as st
import pandas as pd
import io
from datetime import datetime, timedelta
import db
from theme_web import get_theme
from export_utils import botoes_download


def render():
    t = get_theme(st.session_state.get("tema", "Dark Emerald"))

    st.markdown(f"""
    <h2 style="color:{t['C_TEXT']}">🚛 Controle de Frota</h2>
    <p style="color:{t['C_MUTED']}">Histórico e eficiência por veículo</p>
    <hr style="border-color:{t['C_BORDER']};"/>
    """, unsafe_allow_html=True)

    # ── Filtros de período ────────────────────────────────────────
    c1, c2, c3, c4, c5, c6 = st.columns([1.4, 1.4, .6, .6, .6, .8])
    with c1: data_ini = st.date_input("De",  value=datetime(2000,1,1).date(), key="frota_ini")
    with c2: data_fim = st.date_input("Até", value=datetime.now().date(),     key="frota_fim")
    with c3:
        if st.button("30d", key="f30"):
            data_ini = (datetime.now()-timedelta(30)).date()
            data_fim = datetime.now().date()
    with c4:
        if st.button("90d", key="f90"):
            data_ini = (datetime.now()-timedelta(90)).date()
            data_fim = datetime.now().date()
    with c5:
        if st.button("1ano", key="f1a"):
            data_ini = (datetime.now()-timedelta(365)).date()
            data_fim = datetime.now().date()
    with c6:
        if st.button("Tudo", key="ftudo"):
            data_ini = datetime(2000,1,1).date()
            data_fim = datetime.now().date()

    # Filtro por placa
    df_all = db.get_todos_registros()
    if df_all.empty:
        st.info("Nenhum registro encontrado."); return

    placas_disponiveis = ["Todas"] + sorted(df_all["placa"].dropna().unique().tolist())
    placa_sel = st.selectbox("🚛 Filtrar por veículo", placas_disponiveis, key="frota_placa")

    # Aplica filtros
    df = db.get_registros(data_ini=str(data_ini), data_fim=str(data_fim), limit=10000)
    df = df.dropna(subset=["data"])
    if placa_sel != "Todas":
        df = df[df["placa"] == placa_sel]

    if df.empty:
        st.warning("Nenhum registro no período selecionado."); return

    st.caption(f"📅 {data_ini} a {data_fim} · {len(df)} registros · {df['placa'].nunique()} veículo(s)")

    # ── Resumo por veículo ────────────────────────────────────────
    resumo = []
    for placa in sorted(df["placa"].dropna().unique()):
        v = df[df["placa"]==placa]
        custo = v["valor"].sum()
        ltrs  = v["quantidade"].sum()
        diff  = v["horimetro"].max()-v["horimetro"].min() if len(v)>1 else 0
        kml   = diff/ltrs if ltrs>0 else 0
        resumo.append({"Placa":placa, "Registros":len(v),
                       "Custo Total":round(custo,2),
                       "Litros":round(ltrs,2), "km/L":round(kml,2)})
    df_res = pd.DataFrame(resumo)

    # ── Downloads ─────────────────────────────────────────────────
    det = df[["data","placa","produto","responsavel",
              "valor","quantidade","horimetro","categoria"]].copy()
    det["data"] = det["data"].astype(str)
    det.columns = ["Data","Placa","Produto","Condutor",
                   "Valor R$","Litros","Horímetro","Categoria"]

    sheets = {"Resumo": df_res, "Detalhes": det}
    for placa in sorted(df["placa"].dropna().unique())[:10]:
        v = df[df["placa"]==placa][["data","produto","responsavel",
                                    "valor","quantidade","horimetro"]].copy()
        v["data"] = v["data"].astype(str)
        v.columns = ["Data","Produto","Condutor","Valor R$","Litros","Horímetro"]
        sheets[str(placa)[:31]] = v

    botoes_download(st, df_res, "frota",
        f"GESTÃO DE FROTA — {data_ini} a {data_fim}",
        colunas_pdf=["Placa","Registros","Custo Total","Litros","km/L"],
        sheets_excel=sheets)

    st.divider()

    # ── Cards por veículo ─────────────────────────────────────────
    for placa in sorted(df["placa"].dropna().unique()):
        v = df[df["placa"]==placa].sort_values("horimetro")
        custo   = v["valor"].sum()
        ltrs    = v["quantidade"].sum()
        diff_km = v["horimetro"].max()-v["horimetro"].min() if len(v)>1 else 0
        kml     = diff_km/ltrs if ltrs>0 else 0
        cor_kml = "normal" if kml>10 else ("off" if kml>5 else "inverse")

        with st.expander(
                f"🚛  {placa}  —  R$ {custo:,.2f}  |  "
                f"{ltrs:,.0f} L  |  {kml:.2f} km/L"):
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Custo Total", f"R$ {custo:,.2f}")
            c2.metric("🛢️ Litros",      f"{ltrs:,.0f} L")
            c3.metric("📈 km/L",        f"{kml:.2f}", delta_color=cor_kml)

            df_v = v[["data","produto","valor","quantidade",
                       "horimetro","responsavel"]].copy()
            df_v["data"]       = df_v["data"].astype(str)
            df_v["valor"]      = df_v["valor"].map(lambda x: f"R$ {x:.2f}")
            df_v["quantidade"] = df_v["quantidade"].map(lambda x: f"{x:.1f} L")
            df_v["horimetro"]  = df_v["horimetro"].map(lambda x: f"{x:.0f}")
            df_v.columns = ["Data","Produto","Valor","Litros","Horímetro","Condutor"]
            st.dataframe(df_v, use_container_width=True, hide_index=True)

            buf = io.BytesIO()
            df_v.to_excel(buf, index=False)
            st.download_button(
                f"📗 Excel — {placa}", buf.getvalue(),
                f"frota_{placa}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                use_container_width=True, key=f"dl_{placa}")
