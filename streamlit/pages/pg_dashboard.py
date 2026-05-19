# =================================================================
# PAGES/PG_DASHBOARD.PY — Dashboard central
# =================================================================
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import db


def render():
    st.title("📊 Dashboard Central")
    st.caption("Visão consolidada — use os filtros para ajustar o período")

    # ── Filtros de período ────────────────────────────────────────
    with st.container():
        c1, c2, c3, c4, c5, c6, c7 = st.columns([1.2, 1.2, 0.7, 0.7, 0.7, 0.7, 0.7])
        with c1:
            data_ini = st.date_input("De", value=datetime(2000,1,1))
        with c2:
            data_fim = st.date_input("Até", value=datetime.now())
        with c3:
            if st.button("7d"):
                data_ini = datetime.now().date() - timedelta(days=7)
                data_fim = datetime.now().date()
        with c4:
            if st.button("30d"):
                data_ini = datetime.now().date() - timedelta(days=30)
                data_fim = datetime.now().date()
        with c5:
            if st.button("90d"):
                data_ini = datetime.now().date() - timedelta(days=90)
                data_fim = datetime.now().date()
        with c6:
            if st.button("1 ano"):
                data_ini = datetime.now().date() - timedelta(days=365)
                data_fim = datetime.now().date()
        with c7:
            if st.button("Tudo"):
                data_ini = datetime(2000,1,1).date()
                data_fim = datetime.now().date()

    df = db.get_registros(
        data_ini=str(data_ini),
        data_fim=str(data_fim),
        limit=10000)

    if df.empty:
        st.info("Nenhum registro no período selecionado.")
        return

    df = df.dropna(subset=["data"])

    # ── KPIs ─────────────────────────────────────────────────────
    total_val = df["valor"].sum()
    total_vol = df["quantidade"].sum()
    n_placas  = df["placa"].nunique()
    media_pl  = total_val / total_vol if total_vol > 0 else 0

    now = datetime.now()
    mes_atual = df[df["data"].dt.month == now.month]["valor"].sum()
    mes_ant   = df[df["data"].dt.month == (now.month - 1 or 12)]["valor"].sum()
    delta_pct = ((mes_atual - mes_ant) / mes_ant * 100) if mes_ant > 0 else None

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("💰 Investimento Total",
              f"R$ {total_val:,.2f}",
              f"{delta_pct:+.1f}% vs mês ant." if delta_pct else None)
    k2.metric("🛢️ Volume Total",    f"{total_vol:,.0f} L")
    k3.metric("🚛 Frota Ativa",     f"{n_placas} unidades")
    k4.metric("📈 Preço Médio / L", f"R$ {media_pl:.3f}")

    st.divider()

    # ── Evolução mensal ───────────────────────────────────────────
    col_a, col_b = st.columns([3, 1])

    with col_a:
        monthly = df.groupby(df["data"].dt.to_period("M"))["valor"].sum().reset_index()
        monthly["data"] = monthly["data"].dt.to_timestamp()
        fig1 = px.area(monthly, x="data", y="valor",
                       title="Evolução Financeira Mensal",
                       labels={"data": "", "valor": "R$"},
                       color_discrete_sequence=["#3B82F6"])
        fig1.update_layout(paper_bgcolor="#1A1D23", plot_bgcolor="#1A1D23",
                           font_color="#E2E8F0", showlegend=False)
        fig1.update_yaxes(tickprefix="R$")
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        cat = df.groupby("categoria")["valor"].sum().reset_index()
        fig2 = px.pie(cat, names="categoria", values="valor",
                      title="Por Categoria",
                      color_discrete_sequence=["#3B82F6","#EF4444","#F59E0B"])
        fig2.update_layout(paper_bgcolor="#1A1D23", plot_bgcolor="#1A1D23",
                           font_color="#E2E8F0")
        st.plotly_chart(fig2, use_container_width=True)

    # ── Top 10 veículos ───────────────────────────────────────────
    top10 = df.groupby("placa")["valor"].sum().sort_values(
        ascending=True).tail(10).reset_index()
    cores = ["#EF4444" if v == top10["valor"].max()
             else "#3B82F6" for v in top10["valor"]]
    fig3 = px.bar(top10, x="valor", y="placa", orientation="h",
                  title="Top 10 Veículos por Custo Total",
                  labels={"valor": "R$", "placa": ""},
                  color="valor",
                  color_continuous_scale=["#3B82F6","#EF4444"])
    fig3.update_layout(paper_bgcolor="#1A1D23", plot_bgcolor="#1A1D23",
                       font_color="#E2E8F0", showlegend=False,
                       coloraxis_showscale=False)
    fig3.update_xaxes(tickprefix="R$")
    st.plotly_chart(fig3, use_container_width=True)

    # ── KM/L + Empilhado ─────────────────────────────────────────
    col_c, col_d = st.columns(2)

    with col_c:
        medias = []
        for p in df["placa"].unique():
            t = df[df["placa"] == p].sort_values("horimetro")
            if len(t) > 1 and t["quantidade"].sum() > 0:
                kml = (t["horimetro"].max() - t["horimetro"].min()) / t["quantidade"].sum()
                medias.append({"placa": p, "kml": round(kml, 2)})
        if medias:
            df_kml = pd.DataFrame(medias).sort_values("kml", ascending=False).head(10)
            median  = df_kml["kml"].median()
            df_kml["cor"] = df_kml["kml"].apply(
                lambda v: "#22C55E" if v >= median else "#F59E0B")
            fig4 = px.bar(df_kml, x="placa", y="kml",
                          title="Eficiência por Veículo (km/L)",
                          labels={"kml": "km/L", "placa": ""},
                          color="cor", color_discrete_map="identity")
            fig4.update_layout(paper_bgcolor="#1A1D23", plot_bgcolor="#1A1D23",
                               font_color="#E2E8F0", showlegend=False)
            st.plotly_chart(fig4, use_container_width=True)

    with col_d:
        df_piv = df.groupby(
            [df["data"].dt.to_period("M"), "categoria"])["valor"].sum().unstack(
                fill_value=0).reset_index()
        df_piv["data"] = df_piv["data"].dt.to_timestamp()
        fig5 = go.Figure()
        cores_cat = {"ABASTECIMENTO": "#3B82F6", "MANUTENÇÃO": "#EF4444"}
        for cat_name in [c for c in ["ABASTECIMENTO","MANUTENÇÃO"]
                         if c in df_piv.columns]:
            fig5.add_trace(go.Bar(
                x=df_piv["data"], y=df_piv[cat_name],
                name=cat_name,
                marker_color=cores_cat.get(cat_name, "#64748B")))
        fig5.update_layout(barmode="stack",
                           title="Custo Mensal Empilhado",
                           paper_bgcolor="#1A1D23", plot_bgcolor="#1A1D23",
                           font_color="#E2E8F0",
                           yaxis_tickprefix="R$")
        st.plotly_chart(fig5, use_container_width=True)

    # ── Exportar ─────────────────────────────────────────────────
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📊 Exportar CSV", csv,
                           f"relatorio_{datetime.now().strftime('%Y%m%d')}.csv",
                           "text/csv", use_container_width=True)
