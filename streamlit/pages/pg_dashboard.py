# =================================================================
# PAGES/PG_DASHBOARD.PY
# =================================================================
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import db
from theme_web import get_theme
from export_utils import botoes_download


def render():
    t = get_theme(st.session_state.get("tema", "Dark Emerald"))

    st.markdown(f"""
    <h2 style="color:{t['C_TEXT']}">📊 Dashboard Central</h2>
    <p style="color:{t['C_MUTED']}">Visão consolidada · use os filtros para ajustar o período</p>
    <hr style="border-color:{t['C_BORDER']};"/>
    """, unsafe_allow_html=True)

    c1,c2,c3,c4,c5,c6,c7 = st.columns([1.4,1.4,.6,.6,.6,.6,.7])
    with c1: data_ini = st.date_input("De",  value=datetime(2000,1,1).date())
    with c2: data_fim = st.date_input("Até", value=datetime.now().date())
    with c3:
        if st.button("7d"):   data_ini=(datetime.now()-timedelta(7)).date();  data_fim=datetime.now().date()
    with c4:
        if st.button("30d"):  data_ini=(datetime.now()-timedelta(30)).date(); data_fim=datetime.now().date()
    with c5:
        if st.button("90d"):  data_ini=(datetime.now()-timedelta(90)).date(); data_fim=datetime.now().date()
    with c6:
        if st.button("1ano"): data_ini=(datetime.now()-timedelta(365)).date();data_fim=datetime.now().date()
    with c7:
        if st.button("Tudo"): data_ini=datetime(2000,1,1).date(); data_fim=datetime.now().date()

    df = db.get_registros(data_ini=str(data_ini), data_fim=str(data_fim), limit=10000)
    if df.empty:
        st.info("Nenhum registro no período."); return
    df = df.dropna(subset=["data"])

    # ── Downloads ────────────────────────────────────────────────
    df_exp = df[["data","placa","produto","responsavel","valor","quantidade","horimetro","categoria"]].copy()
    df_exp["data"] = df_exp["data"].astype(str)
    df_exp.columns = ["Data","Placa","Produto","Condutor","Valor R$","Litros","Horímetro","Categoria"]

    resumo = df.groupby("placa").agg(total=("valor","sum"),litros=("quantidade","sum"),n=("valor","count")).reset_index()
    resumo.columns = ["Placa","Total R$","Litros","Registros"]

    monthly_exp = df.groupby(df["data"].dt.to_period("M"))["valor"].sum().reset_index()
    monthly_exp["data"] = monthly_exp["data"].astype(str)
    monthly_exp.columns = ["Mês","Total R$"]

    botoes_download(st, df_exp, "dashboard",
        f"DASHBOARD KITAGAWA | {data_ini} a {data_fim}",
        colunas_pdf=["Data","Placa","Produto","Valor R$","Litros","Categoria"],
        sheets_excel={"Registros": df_exp, "Por Veículo": resumo, "Mensal": monthly_exp})

    # ── KPIs ─────────────────────────────────────────────────────
    total_val = df["valor"].sum()
    total_vol = df["quantidade"].sum()
    n_placas  = df["placa"].nunique()
    media_pl  = total_val/total_vol if total_vol>0 else 0
    now = datetime.now()
    mes_a = df[df["data"].dt.month==now.month]["valor"].sum()
    mes_b = df[df["data"].dt.month==(now.month-1 or 12)]["valor"].sum()
    delta = f"{(mes_a-mes_b)/mes_b*100:+.1f}% vs mês ant." if mes_b>0 else None

    k1,k2,k3,k4 = st.columns(4)
    k1.metric("💰 Investimento Total", f"R$ {total_val:,.2f}", delta)
    k2.metric("🛢️ Volume Total",       f"{total_vol:,.0f} L")
    k3.metric("🚛 Frota Ativa",        f"{n_placas} unidades")
    k4.metric("📈 Preço Médio / L",    f"R$ {media_pl:.3f}")

    st.divider()

    col_a, col_b = st.columns([3,1])
    with col_a:
        m = df.groupby(df["data"].dt.to_period("M"))["valor"].sum().reset_index()
        m["data"] = m["data"].dt.to_timestamp()
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=m["data"], y=m["valor"],
            fill="tozeroy", fillcolor="rgba(16,185,129,0.15)",
            line=dict(color=t["C_ACCENT"], width=2.5),
            mode="lines+markers", marker=dict(size=6)))
        fig1.update_layout(title=dict(text="Evolução Financeira Mensal",font=dict(color=t["C_TEXT"],size=14)),
            paper_bgcolor=t["C_SURFACE"],plot_bgcolor=t["C_SURFACE"],font=dict(color=t["C_MUTED"]),
            yaxis=dict(tickprefix="R$",gridcolor=t["C_BORDER"]),xaxis=dict(gridcolor=t["C_BORDER"]),
            showlegend=False,margin=dict(l=0,r=0,t=40,b=0))
        st.plotly_chart(fig1, use_container_width=True)
    with col_b:
        cat = df.groupby("categoria")["valor"].sum().reset_index()
        fig2 = px.pie(cat,names="categoria",values="valor",title="Por Categoria",
            color_discrete_sequence=[t["C_ACCENT"],t["C_DANGER"],t["C_WARNING"],t["C_SUCCESS"]])
        fig2.update_layout(paper_bgcolor=t["C_SURFACE"],plot_bgcolor=t["C_SURFACE"],
            font=dict(color=t["C_TEXT"]),title=dict(font=dict(color=t["C_TEXT"])),margin=dict(l=0,r=0,t=40,b=0))
        fig2.update_traces(textfont_color="white")
        st.plotly_chart(fig2, use_container_width=True)

    top10 = df.groupby("placa")["valor"].sum().sort_values(ascending=True).tail(10).reset_index()
    cores = [t["C_DANGER"] if v==top10["valor"].max() else t["C_ACCENT"] for v in top10["valor"]]
    fig3 = go.Figure(go.Bar(x=top10["valor"],y=top10["placa"],orientation="h",
        marker_color=cores,text=[f"R${v:,.0f}" for v in top10["valor"]],
        textposition="outside",textfont=dict(color=t["C_TEXT"],size=10)))
    fig3.update_layout(title=dict(text="Top Veículos por Custo Total",font=dict(color=t["C_TEXT"],size=14)),
        paper_bgcolor=t["C_SURFACE"],plot_bgcolor=t["C_SURFACE"],font=dict(color=t["C_MUTED"]),
        xaxis=dict(tickprefix="R$",gridcolor=t["C_BORDER"]),yaxis=dict(gridcolor=t["C_BORDER"]),
        showlegend=False,margin=dict(l=0,r=0,t=40,b=0))
    st.plotly_chart(fig3, use_container_width=True)

    col_c, col_d = st.columns(2)
    with col_c:
        medias=[]
        for p in df["placa"].unique():
            v=df[df["placa"]==p].sort_values("horimetro")
            if len(v)>1 and v["quantidade"].sum()>0:
                kml=(v["horimetro"].max()-v["horimetro"].min())/v["quantidade"].sum()
                medias.append({"placa":p,"kml":round(kml,2)})
        if medias:
            dk=pd.DataFrame(medias).sort_values("kml",ascending=False).head(10)
            med=dk["kml"].median()
            fig4=go.Figure(go.Bar(x=dk["placa"],y=dk["kml"],
                marker_color=[t["C_SUCCESS"] if v>=med else t["C_WARNING"] for v in dk["kml"]],
                text=[f"{v:.1f}" for v in dk["kml"]],textposition="outside",
                textfont=dict(color=t["C_TEXT"],size=9)))
            fig4.update_layout(title=dict(text="Eficiência por Veículo (km/L)",font=dict(color=t["C_TEXT"],size=13)),
                paper_bgcolor=t["C_SURFACE"],plot_bgcolor=t["C_SURFACE"],font=dict(color=t["C_MUTED"]),
                yaxis=dict(title="km/L",gridcolor=t["C_BORDER"]),xaxis=dict(gridcolor=t["C_BORDER"]),
                showlegend=False,margin=dict(l=0,r=0,t=40,b=0))
            st.plotly_chart(fig4, use_container_width=True)
    with col_d:
        dp=df.groupby([df["data"].dt.to_period("M"),"categoria"])["valor"].sum().unstack(fill_value=0)
        dp.index=dp.index.to_timestamp()
        fig5=go.Figure()
        for cn,cc in [("ABASTECIMENTO",t["C_ACCENT"]),("MANUTENÇÃO",t["C_DANGER"])]:
            if cn in dp.columns:
                fig5.add_trace(go.Bar(x=dp.index,y=dp[cn],name=cn,marker_color=cc,opacity=0.85))
        fig5.update_layout(barmode="stack",title=dict(text="Custo Mensal Empilhado",font=dict(color=t["C_TEXT"],size=13)),
            paper_bgcolor=t["C_SURFACE"],plot_bgcolor=t["C_SURFACE"],font=dict(color=t["C_MUTED"]),
            yaxis=dict(tickprefix="R$",gridcolor=t["C_BORDER"]),xaxis=dict(gridcolor=t["C_BORDER"]),
            legend=dict(font=dict(color=t["C_TEXT"])),margin=dict(l=0,r=0,t=40,b=0))
        st.plotly_chart(fig5, use_container_width=True)
