# =================================================================
# PAGES/PG_NOVO_REGISTRO.PY
# =================================================================
import streamlit as st
from datetime import datetime
import db


def render():
    st.title("➕ Lançamento Manual")
    st.caption("Registre um abastecimento ou manutenção")

    veiculos   = db.get_veiculos()["placa"].tolist()
    condutores = db.get_condutores()["nome"].tolist()

    if not veiculos:
        st.warning("Cadastre ao menos um veículo antes de lançar.")
        return

    c1, c2 = st.columns(2)
    data      = c1.date_input("Data", value=datetime.now())
    placa     = c1.selectbox("Veículo (Placa)", veiculos)
    condutor  = c2.selectbox("Condutor", condutores or ["—"])
    produto   = c2.selectbox("Produto", ["DIESEL S10","DIESEL S500","GASOLINA",
                              "ETANOL","ARLA 32","ÓLEO","FILTRO","PNEU","OUTRO"])
    qtd       = c1.number_input("Quantidade (L)", min_value=0.0, step=0.1)
    valor     = c1.number_input("Valor Total (R$)", min_value=0.0, step=0.01)
    horimetro = c2.number_input("Horímetro / KM", min_value=0.0, step=1.0)

    from etl_web import identify_category
    categoria = identify_category(produto)
    st.info(f"Categoria detectada: **{categoria}**")

    if st.button("➕ FINALIZAR LANÇAMENTO", type="primary", use_container_width=True):
        hv = f"MAN-{datetime.now().timestamp()}-{placa}"
        if db.inserir_registro(str(data), produto.upper(), condutor.upper(),
                                placa.upper(), "MANUAL", valor, qtd,
                                horimetro, categoria, "LANÇAMENTO MANUAL", hv):
            st.success("Registro salvo com sucesso!")
        else:
            st.error("Erro ao salvar. Registro duplicado?")
