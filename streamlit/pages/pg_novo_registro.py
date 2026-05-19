# =================================================================
# PAGES/PG_NOVO_REGISTRO.PY
# =================================================================
import streamlit as st
from datetime import datetime
import db
from etl_web import identify_category
from theme_web import get_theme


def render():
    t = get_theme(st.session_state.get("tema", "Dark Emerald"))

    st.markdown(f"""
    <h2 style="color:{t['C_TEXT']}">➕ Lançamento Manual</h2>
    <p style="color:{t['C_MUTED']}">Registre um abastecimento ou manutenção</p>
    <hr style="border-color:{t['C_BORDER']};"/>
    """, unsafe_allow_html=True)

    df_veic = db.get_veiculos()
    df_cond = db.get_condutores()
    veiculos   = df_veic["placa"].tolist() if not df_veic.empty else []
    condutores = df_cond["nome"].tolist()  if not df_cond.empty else []

    if not veiculos:
        st.warning("Cadastre ao menos um veículo antes de lançar.")
        return

    c1, c2 = st.columns(2)
    data      = c1.date_input("📅 Data", value=datetime.now().date())
    placa     = c1.selectbox("🚛 Veículo (Placa)", veiculos)
    condutor  = c2.selectbox("👤 Condutor", condutores or ["—"])
    produto   = c2.selectbox("⛽ Produto/Combustível",
                  ["DIESEL S10","DIESEL S500","GASOLINA","ETANOL",
                   "ARLA 32","ÓLEO","FILTRO","PNEU","OUTRO"])
    qtd   = c1.number_input("📦 Quantidade (L)",    min_value=0.0, step=0.1,  format="%.2f")
    valor = c1.number_input("💰 Valor Total (R$)",  min_value=0.0, step=0.01, format="%.2f")
    hor   = c2.number_input("📏 Horímetro / KM",    min_value=0.0, step=1.0,  format="%.1f")

    categoria = identify_category(produto)
    st.info(f"Categoria detectada automaticamente: **{categoria}**")

    if st.button("➕  FINALIZAR LANÇAMENTO", type="primary",
                  use_container_width=True):
        hv = f"MAN-{datetime.now().timestamp()}-{placa}"
        if db.inserir_registro(
                str(data), produto.upper(), condutor.upper(),
                placa.upper(), "MANUAL", valor, qtd, hor,
                categoria, "LANÇAMENTO MANUAL", hv):
            st.success("✅ Registro salvo com sucesso!")
            st.balloons()
        else:
            st.error("Erro ao salvar. Registro duplicado?")
