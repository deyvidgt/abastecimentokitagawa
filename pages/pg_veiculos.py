# =================================================================
# PAGES/PG_VEICULOS.PY
# =================================================================
import streamlit as st
import db

TIPOS = ["Caminhão","Caminhonete","Trator","Van","Leve",
         "Máquina Agrícola","Drone","Outro"]


def render():
    st.title("🚗 Cadastro de Veículos")

    # Formulário de cadastro
    with st.expander("➕ Novo veículo", expanded=True):
        c1, c2, c3 = st.columns(3)
        placa  = c1.text_input("Placa / Identificador")
        modelo = c2.text_input("Modelo / Descrição")
        tipo   = c3.selectbox("Tipo", TIPOS)

        if st.button("💾 Cadastrar", type="primary"):
            if not placa or not modelo:
                st.warning("Placa e Modelo são obrigatórios.")
            elif db.inserir_veiculo(placa, modelo, tipo):
                st.success(f"Veículo {placa.upper()} cadastrado!")
                st.rerun()
            else:
                st.error("Placa já existe.")

    st.divider()

    df = db.get_veiculos()
    if df.empty:
        st.info("Nenhum veículo cadastrado.")
        return

    st.dataframe(df[["placa","modelo","tipo","status"]],
                 use_container_width=True, hide_index=True)

    # Editar
    with st.expander("✏️ Editar veículo"):
        placas = df["placa"].tolist()
        sel    = st.selectbox("Selecione a placa", placas)
        row    = df[df["placa"] == sel].iloc[0]
        c1, c2 = st.columns(2)
        nova_placa  = c1.text_input("Nova placa",  value=row["placa"])
        novo_modelo = c1.text_input("Modelo",       value=row["modelo"])
        novo_tipo   = c2.selectbox("Tipo", TIPOS,
                        index=TIPOS.index(row["tipo"]) if row["tipo"] in TIPOS else 0)
        novo_status = c2.selectbox("Status", ["Ativo","Inativo","Manutenção"],
                        index=["Ativo","Inativo","Manutenção"].index(row["status"])
                              if row["status"] in ["Ativo","Inativo","Manutenção"] else 0)
        if st.button("💾 Salvar edição", type="primary"):
            if db.atualizar_veiculo(sel, nova_placa.upper(), novo_modelo.upper(),
                                     novo_tipo, novo_status):
                st.success("Veículo atualizado!")
                st.rerun()
            else:
                st.error("Não foi possível salvar.")

    # Excluir
    with st.expander("🗑️ Excluir veículo"):
        sel_del = st.selectbox("Placa a excluir", df["placa"].tolist(), key="del_v")
        if st.button("🗑️ Excluir", type="secondary"):
            if db.excluir_veiculo(sel_del):
                st.success(f"{sel_del} removido.")
                st.rerun()
            else:
                st.error("Não foi possível excluir.")
