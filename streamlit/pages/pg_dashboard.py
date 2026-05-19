# =================================================================
# PAGES/PG_DASHBOARD.PY — Dashboard central
# =================================================================
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import db
from theme_web import get_theme


def render():
    t = get_theme(st.session_state.get("tema", "Dark Emerald"))

    st.markdown(f"""
    <h2 style="color:{t['C_TEXT']};margin-bottom:2px;">📊 Dashboard Central</h2>
    <p style="color:{t['C_MUTED']};margin-top:0;">
        Visão consolidada · use os filtros para ajustar o período</p>
    <hr style="border-color:{t['C_BORDER']};"/>
    """, unsafe_allow_html=True)

    # ── Filtros ───────────────────────────────────────────────────
    c1, c2, c3, c4, c5, c6, c7 = st.columns([1.4, 1.4, .6, .6, .6, .6, .7])
    with c1: data_ini = st.date_input("De",   value=datetime(2000,1,1).date())
    with c2: data_fim = st.date_input("Até",  value=datetime.now().date())
    with c3:
        if st.button("7d"):
            data_ini = (datetime.now()-timedelta(days=7)).date()
            data_fim = datetime.now().date()
    with c4:
        if st.button("30d"):
            data_ini = (datetime.now()-timedelta(days=30)).date()
            data_fim = datetime.now().date()
    with c5:
        if st.button("90d"):
            data_ini = (datetime.now()-timedelta(days=90)).date()
            data_fim = datetime.now().date()
    with c6:
        if st.button("1 ano"):
            data_ini = (datetime.now()-timedelta(days=365)).date()
            data_fim = datetime.now().date()
    with c7:
        if st.button("Tudo"):
            data_ini = datetime(2000,1,1).date()
            data_fim = datetime.now().date()

    # Exportar
    col_pdf, col_xls, _ = st.columns([1, 1, 6])

    df = db.get_registros(data_ini=str(data_ini), data_fim=str(data_fim), limit=10000)

    if df.empty:
        st.info("Nenhum registro no período. Importe planilhas ou crie registros.")
        return

    df = df.dropna(subset=["data"])

    # Exportar CSV
    with col_pdf:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📄 CSV", csv,
            f"relatorio_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv", use_container_width=True)

    # ── KPIs ─────────────────────────────────────────────────────
    total_val = df["valor"].sum()
    total_vol = df["quantidade"].sum()
    n_placas  = df["placa"].nunique()
    media_pl  = total_val / total_vol if total_vol > 0 else 0

    now = datetime.now()
    mes_atual = df[df["data"].dt.month == now.month]["valor"].sum()
    mes_ant   = df[df["data"].dt.month == (now.month-1 or 12)]["valor"].sum()
    delta_pct = ((mes_atual-mes_ant)/mes_ant*100) if mes_ant > 0 else None
    delta_str = (f"{delta_pct:+.1f}% vs mês ant." if delta_pct else None)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("💰 Investimento Total", f"R$ {total_val:,.2f}", delta_str)
    k2.metric("🛢️ Volume Total",       f"{total_vol:,.0f} L")
    k3.metric("🚛 Frota Ativa",        f"{n_placas} unidades")
    k4.metric("📈 Preço Médio / L",    f"R$ {media_pl:.3f}")

    st.divider()

    # ── Evolução mensal + pizza ───────────────────────────────────
    col_a, col_b = st.columns([3, 1])

    with col_a:
        monthly = df.groupby(df["data"].dt.to_period("M"))["valor"].sum().reset_index()
        monthly["data"] = monthly["data"].dt.to_timestamp()
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=monthly["data"], y=monthly["valor"],
            fill="tozeroy", fillcolor="rgba(59,130,246,0.15)",
            line=dict(color=t["C_ACCENT"], width=2.5),
            text=[f"R${v/1000:.1f}k" for v in monthly["valor"]],
            textposition="top center", textfont=dict(color=t["C_TEXT"], size=10),
            mode="lines+markers+text"))
        fig1.update_layout(
            title=dict(text="Evolução Financeira Mensal",
                       font=dict(color=t["C_TEXT"], size=14)),
            paper_bgcolor=t["C_SURFACE"], plot_bgcolor=t["C_SURFACE"],
            font=dict(color=t["C_MUTED"]),
            yaxis=dict(tickprefix="R$", gridcolor=t["C_BORDER"]),
            xaxis=dict(gridcolor=t["C_BORDER"]),
            showlegend=False, margin=dict(l=0,r=0,t=40,b=0))
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        cat = df.groupby("categoria")["valor"].sum().reset_index()
        fig2 = px.pie(cat, names="categoria", values="valor",
                      title="Por Categoria",
                      color_discrete_sequence=[t["C_ACCENT"],t["C_DANGER"],
                                               t["C_WARNING"],t["C_SUCCESS"]])
        fig2.update_layout(
            paper_bgcolor=t["C_SURFACE"], plot_bgcolor=t["C_SURFACE"],
            font=dict(color=t["C_TEXT"]),
            title=dict(font=dict(color=t["C_TEXT"])),
            margin=dict(l=0,r=0,t=40,b=0))
        fig2.update_traces(textfont_color="white")
        st.plotly_chart(fig2, use_container_width=True)

    # ── Top 10 veículos ───────────────────────────────────────────
    top10 = df.groupby("placa")["valor"].sum().sort_values(ascending=True).tail(10).reset_index()
    cores = [t["C_DANGER"] if v == top10["valor"].max()
             else t["C_ACCENT"] for v in top10["valor"]]
    fig3 = go.Figure(go.Bar(
        x=top10["valor"], y=top10["placa"],
        orientation="h",
        marker_color=cores,
        text=[f"R${v:,.0f}" for v in top10["valor"]],
        textposition="outside",
        textfont=dict(color=t["C_TEXT"], size=10)))
    fig3.update_layout(
        title=dict(text="Top Veículos por Custo Total",
                   font=dict(color=t["C_TEXT"], size=14)),
        paper_bgcolor=t["C_SURFACE"], plot_bgcolor=t["C_SURFACE"],
        font=dict(color=t["C_MUTED"]),
        xaxis=dict(tickprefix="R$", gridcolor=t["C_BORDER"]),
        yaxis=dict(gridcolor=t["C_BORDER"]),
        showlegend=False, margin=dict(l=0,r=0,t=40,b=0))
    st.plotly_chart(fig3, use_container_width=True)

    # ── KM/L + Empilhado ─────────────────────────────────────────
    col_c, col_d = st.columns(2)

    with col_c:
        medias = []
        for p in df["placa"].unique():
            v = df[df["placa"]==p].sort_values("horimetro")
            if len(v)>1 and v["quantidade"].sum()>0:
                kml = (v["horimetro"].max()-v["horimetro"].min())/v["quantidade"].sum()
        if medias:
            df_kml = pd.DataFrame(medias).sort_values("kml",ascending=False).head(10)
            median  = df_kml["kml"].median()
            cores_kml = [t["C_SUCCESS"] if v>=median else t["C_WARNING"]
                         for v in df_kml["kml"]]
            fig4 = go.Figure(go.Bar(
                x=df_kml["placa"], y=df_kml["kml"],
                marker_color=cores_kml,
                text=[f"{v:.1f}" for v in df_kml["kml"]],
                textposition="outside",
                textfont=dict(color=t["C_TEXT"], size=9)))
            fig4.update_layout(
                title=dict(text="Eficiência por Veículo (km/L)",
                           font=dict(color=t["C_TEXT"], size=13)),
                paper_bgcolor=t["C_SURFACE"], plot_bgcolor=t["C_SURFACE"],
                font=dict(color=t["C_MUTED"]),
                yaxis=dict(title="km/L", gridcolor=t["C_BORDER"]),
                xaxis=dict(gridcolor=t["C_BORDER"]),
                showlegend=False, margin=dict(l=0,r=0,t=40,b=0))
            st.plotly_chart(fig4, use_container_width=True)

    with col_d:
        df_piv = df.groupby(
            [df["data"].dt.to_period("M"),"categoria"])["valor"].sum().unstack(fill_value=0)
        df_piv.index = df_piv.index.to_timestamp()
        fig5 = go.Figure()
        cores_cat = {"ABASTECIMENTO":t["C_ACCENT"],"MANUTENÇÃO":t["C_DANGER"]}
        bottoms = None
        for cat_name in [c for c in ["ABASTECIMENTO","MANUTENÇÃO"]
                         if c in df_piv.columns]:
            fig5.add_trace(go.Bar(
                x=df_piv.index, y=df_piv[cat_name],
                name=cat_name,
                marker_color=cores_cat.get(cat_name, t["C_WARNING"]),
                opacity=0.85))
        fig5.update_layout(
            barmode="stack",
            title=dict(text="Custo Mensal Empilhado",
                       font=dict(color=t["C_TEXT"], size=13)),
            paper_bgcolor=t["C_SURFACE"], plot_bgcolor=t["C_SURFACE"],
            font=dict(color=t["C_MUTED"]),
            yaxis=dict(tickprefix="R$", gridcolor=t["C_BORDER"]),
            xaxis=dict(gridcolor=t["C_BORDER"]),
            legend=dict(font=dict(color=t["C_TEXT"])),
            margin=dict(l=0,r=0,t=40,b=0))
        st.plotly_chart(fig5, use_container_width=True)
