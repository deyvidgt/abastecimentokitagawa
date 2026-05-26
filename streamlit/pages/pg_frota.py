# =================================================================
# PAGES/PG_FROTA.PY
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
    c1,c2,c3,c4,c5,c6 = st.columns([1.4,1.4,.6,.6,.6,.8])
    with c1: data_ini = st.date_input("De",  value=datetime(2000,1,1).date(), key="frota_ini", format="DD/MM/YYYY")
    with c2: data_fim = st.date_input("Até", value=datetime.now().date(),     key="frota_fim", format="DD/MM/YYYY")
    with c3:
        if st.button("30d",  key="f30"):   data_ini=(datetime.now()-timedelta(30)).date();  data_fim=datetime.now().date()
    with c4:
        if st.button("90d",  key="f90"):   data_ini=(datetime.now()-timedelta(90)).date();  data_fim=datetime.now().date()
    with c5:
        if st.button("1ano", key="f1a"):   data_ini=(datetime.now()-timedelta(365)).date(); data_fim=datetime.now().date()
    with c6:
        if st.button("Tudo", key="ftudo"): data_ini=datetime(2000,1,1).date(); data_fim=datetime.now().date()

    # Carrega veículos para pegar modelo e frota
    df_veic = db.get_veiculos()
    veic_info = {}
    if not df_veic.empty:
        for _, row in df_veic.iterrows():
            veic_info[row["placa"]] = {
                "modelo": row.get("modelo", "") or "",
                "frota":  row.get("frota",  "") or "",
                "tipo":   row.get("tipo",   "") or "",
            }

    df_all = db.get_todos_registros()
    if df_all.empty:
        st.info("Nenhum registro encontrado."); return

    # Filtro por veículo — mostra placa + modelo
    def label_veiculo(placa):
        info = veic_info.get(placa, {})
        modelo = info.get("modelo", "")
        frota  = info.get("frota",  "")
        partes = [placa]
        if modelo: partes.append(modelo)
        if frota:  partes.append(f"Frota: {frota}")
        return " — ".join(partes)

    placas_disp = sorted(df_all["placa"].dropna().unique().tolist())
    labels      = ["Todas"] + [label_veiculo(p) for p in placas_disp]
    placa_map   = {label_veiculo(p): p for p in placas_disp}

    sel_label = st.selectbox("🚛 Filtrar por veículo", labels, key="frota_placa")
    placa_sel = placa_map.get(sel_label, None)

    df = db.get_registros(data_ini=str(data_ini), data_fim=str(data_fim), limit=10000)
    df = df.dropna(subset=["data"])
    if placa_sel:
        df = df[df["placa"] == placa_sel]

    if df.empty:
        st.warning("Nenhum registro no período selecionado."); return

    st.caption(
        f"📅 {data_ini.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')} "
        f"· {len(df)} registros · {df['placa'].nunique()} veículo(s)")

    # ── Resumo por veículo ─────────────────────────────────────────
    resumo = []
    for placa in sorted(df["placa"].dropna().unique()):
        v     = df[df["placa"] == placa]
        info  = veic_info.get(placa, {})
        custo = v["valor"].sum()
        ltrs  = v["quantidade"].sum()
        diff  = v["horimetro"].max() - v["horimetro"].min() if len(v) > 1 else 0
        kml   = diff / ltrs if ltrs > 0 else 0
        resumo.append({
            "Placa":       placa,
            "Modelo":      info.get("modelo", "—"),
            "Frota":       info.get("frota",  "—"),
            "Registros":   len(v),
            "Custo Total": round(custo, 2),
            "Litros":      round(ltrs, 2),
            "km/L":        round(kml, 2),
        })
    df_res = pd.DataFrame(resumo)

    # ── Downloads ─────────────────────────────────────────────────
    det = df[["data_fmt","placa","produto","responsavel",
              "valor","quantidade","horimetro","categoria"]].copy()
    det.columns = ["Data","Placa","Produto","Condutor",
                   "Valor R$","Litros","Horímetro","Categoria"]

    sheets = {"Resumo": df_res, "Detalhes": det}
    for placa in sorted(df["placa"].dropna().unique())[:10]:
        v = df[df["placa"] == placa][["data_fmt","produto","responsavel",
                                      "valor","quantidade","horimetro"]].copy()
        v.columns = ["Data","Produto","Condutor","Valor R$","Litros","Horímetro"]
        sheets[str(placa)[:31]] = v

    botoes_download(st, df_res, "frota",
        f"GESTÃO DE FROTA — {data_ini.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}",
        colunas_pdf=["Placa","Modelo","Frota","Custo Total","Litros","km/L"],
        sheets_excel=sheets)

    st.divider()

    # ── Cards por veículo ─────────────────────────────────────────
    for placa in sorted(df["placa"].dropna().unique()):
        v      = df[df["placa"] == placa].sort_values("horimetro")
        info   = veic_info.get(placa, {})
        modelo = info.get("modelo", "")
        frota  = info.get("frota",  "")
        custo   = v["valor"].sum()
        ltrs    = v["quantidade"].sum()
        diff_km = v["horimetro"].max() - v["horimetro"].min() if len(v) > 1 else 0
        kml     = diff_km / ltrs if ltrs > 0 else 0
        cor_kml = "normal" if kml > 10 else ("off" if kml > 5 else "inverse")

        # Título do card com placa + modelo + frota
        titulo = f"🚛  {placa}"
        if modelo: titulo += f"  |  {modelo}"
        if frota:  titulo += f"  |  Frota: {frota}"
        titulo += f"  —  R$ {custo:,.2f}  |  {ltrs:,.0f} L  |  {kml:.2f} km/L"

        with st.expander(titulo):
            # Info do veículo
            if modelo or frota:
                ci1, ci2, ci3 = st.columns(3)
                ci1.markdown(f"**Placa:** {placa}")
                if modelo: ci2.markdown(f"**Modelo:** {modelo}")
                if frota:  ci3.markdown(f"**Nº Frota:** {frota}")
                st.divider()

            c1,c2,c3 = st.columns(3)
            c1.metric("💰 Custo Total", f"R$ {custo:,.2f}")
            c2.metric("🛢️ Litros",      f"{ltrs:,.0f} L")
            c3.metric("📈 km/L",        f"{kml:.2f}", delta_color=cor_kml)

            df_v = v[["data_fmt","produto","valor","quantidade",
                       "horimetro","responsavel"]].copy()
            df_v["valor"]      = df_v["valor"].map(lambda x: f"R$ {x:.2f}")
            df_v["quantidade"] = df_v["quantidade"].map(lambda x: f"{x:.1f} L")
            df_v["horimetro"]  = df_v["horimetro"].map(lambda x: f"{x:.0f}")
            df_v.columns = ["Data","Produto","Valor","Litros","Horímetro","Condutor"]
            st.dataframe(df_v, use_container_width=True, hide_index=True)

            buf = io.BytesIO()
            df_v.to_excel(buf, index=False)
            nome_arq = f"frota_{placa}"
            if modelo: nome_arq += f"_{modelo.replace(' ','_')}"
            st.download_button(
                f"📗 Excel — {placa}" + (f" ({modelo})" if modelo else ""),
                buf.getvalue(),
                f"{nome_arq}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                use_container_width=True, key=f"dl_{placa}")
