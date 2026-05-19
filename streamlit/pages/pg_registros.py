# =================================================================
# PAGES/PG_REGISTROS.PY
# =================================================================
import streamlit as st
import db


def render():
    st.title("📋 Registros")
    st.caption("Pesquise, edite ou exclua lançamentos")

    # Filtros
    with st.expander("🔍 Filtros", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        placa_f   = c1.text_input("Placa / ID")
        produto_f = c2.text_input("Produto")
        data_ini  = c3.date_input("De",  value=None)
        data_fim  = c4.date_input("Até", value=None)

    df = db.get_registros(
        data_ini=str(data_ini) if data_ini else None,
        data_fim=str(data_fim) if data_fim else None,
        placa=placa_f or None,
        produto=produto_f or None)

    st.caption(f"{len(df)} registro(s) encontrado(s)")

    if df.empty:
        st.info("Nenhum registro encontrado.")
        return

    # Tabela
    df_show = df[["id","data","placa","produto","responsavel",
                  "valor","quantidade","horimetro","categoria"]].copy()
    df_show["data"]       = df_show["data"].astype(str)
    df_show["valor"]      = df_show["valor"].map(lambda x: f"{x:.2f}")
    df_show["quantidade"] = df_show["quantidade"].map(lambda x: f"{x:.1f}")
    df_show["horimetro"]  = df_show["horimetro"].map(lambda x: f"{x:.0f}")
    df_show.columns = ["ID","Data","Placa","Produto","Condutor",
                       "Valor R$","Litros","Horímetro","Categoria"]
    st.dataframe(df_show, use_container_width=True, hide_index=True)

    st.divider()

    # Editar
    with st.expander("✏️ Editar registro"):
        reg_id = st.number_input("ID do registro", min_value=1, step=1)
        reg_row = df[df["id"] == reg_id]
        if not reg_row.empty:
            r = reg_row.iloc[0]
            veiculos   = db.get_veiculos()["placa"].tolist()
            condutores = db.get_condutores()["nome"].tolist()
            c1, c2 = st.columns(2)
            nova_data  = c1.date_input("Data", value=r["data"])
            nova_placa = c1.selectbox("Placa", veiculos,
                index=veiculos.index(r["placa"]) if r["placa"] in veiculos else 0)
            novo_prod  = c2.selectbox("Produto",
                ["DIESEL S10","DIESEL S500","GASOLINA","ETANOL",
                 "ARLA 32","ÓLEO","FILTRO","PNEU","OUTRO"],
                index=0)
            novo_cond  = c2.selectbox("Condutor", condutores,
                index=condutores.index(r["responsavel"])
                      if r["responsavel"] in condutores else 0)
            novo_val   = c1.number_input("Valor R$",   value=float(r["valor"]),   step=0.01)
            nova_qtd   = c1.number_input("Litros",      value=float(r["quantidade"]), step=0.1)
            novo_hor   = c2.number_input("Horímetro",   value=float(r["horimetro"]),  step=1.0)
            nova_cat   = c2.selectbox("Categoria", ["ABASTECIMENTO","MANUTENÇÃO"],
                index=0 if r["categoria"] == "ABASTECIMENTO" else 1)

            if st.button("💾 Salvar alterações", type="primary"):
                if db.atualizar_registro(reg_id, str(nova_data), novo_prod,
                                          novo_cond, nova_placa, novo_val,
                                          nova_qtd, novo_hor, nova_cat):
                    st.success(f"Registro #{reg_id} atualizado!")
                    st.rerun()
                else:
                    st.error("Não foi possível salvar.")

    # Excluir
    with st.expander("🗑️ Excluir registro"):
        del_id = st.number_input("ID a excluir", min_value=1, step=1, key="del_id")
        if st.button("🗑️ Excluir", type="secondary"):
            if db.excluir_registro(int(del_id)):
                st.success(f"Registro #{del_id} excluído.")
                st.rerun()
            else:
                st.error("Não foi possível excluir.")
