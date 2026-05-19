# =================================================================
# PAGES/PG_FROTA.PY
# =================================================================
import streamlit as st
import pandas as pd
import plotly.express as px
import db


def render():
    st.title("🚛 Controle de Frota")
    st.caption("Histórico e eficiência por veículo")

    df = db.get_todos_registros()
    if df.empty:
        st.info("Nenhum registro encontrado.")
        return

    for placa in sorted(df["placa"].dropna().unique()):
        v = df[df["placa"] == placa].sort_values("horimetro")
        custo   = v["valor"].sum()
        ltrs    = v["quantidade"].sum()
        diff_km = v["horimetro"].max() - v["horimetro"].min() if len(v) > 1 else 0
        kml     = diff_km / ltrs if ltrs > 0 else 0
        cor_kml = "normal" if kml > 10 else ("off" if kml > 5 else "inverse")

        with st.expander(f"🚛  {placa}  —  R$ {custo:,.2f}", expanded=False):
            c1, c2, c3 = st.columns(3)
            c1.metric("💰 Custo Total",   f"R$ {custo:,.2f}")
            c2.metric("🛢️ Litros",        f"{ltrs:,.0f} L")
            c3.metric("📈 Eficiência",    f"{kml:.2f} km/L",
                      delta_color=cor_kml)

            df_v = v[["data","produto","valor","quantidade",
                       "horimetro","responsavel"]].copy()
            df_v["data"]       = df_v["data"].astype(str)
            df_v["valor"]      = df_v["valor"].map(lambda x: f"R$ {x:.2f}")
            df_v["quantidade"] = df_v["quantidade"].map(lambda x: f"{x:.1f} L")
            df_v["horimetro"]  = df_v["horimetro"].map(lambda x: f"{x:.0f}")
            df_v.columns       = ["Data","Produto","Valor","Litros","Horímetro","Condutor"]
            st.dataframe(df_v, use_container_width=True, hide_index=True)
