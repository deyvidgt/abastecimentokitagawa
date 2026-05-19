# =================================================================
# PAGES/PG_IMPORTACAO.PY — Importação de planilhas Excel
# =================================================================
import streamlit as st
import pandas as pd
import db
from etl_web import ProcessorETL


def render():
    st.title("📥 Importar Planilhas")
    st.caption("Faça upload de arquivos Excel (.xlsx / .xls)")

    arquivos = st.file_uploader(
        "Selecione os arquivos Excel",
        type=["xlsx","xls"],
        accept_multiple_files=True)

    if not arquivos:
        return

    if st.button("▶️ PROCESSAR ARQUIVOS", type="primary", use_container_width=True):
        placas_conhecidas = set(db.get_veiculos()["placa"].tolist())
        total = {"inseridos": 0, "duplicados": 0, "erros": 0}

        barra = st.progress(0, text="Iniciando...")
        log   = st.empty()
        linhas_log = []

        for i, arq in enumerate(arquivos):
            barra.progress((i) / len(arquivos), text=f"Processando {arq.name}...")
            linhas_log.append(f"▶ {arq.name}")

            res = ProcessorETL.process_uploaded_file(arq, arq.name, db, placas_conhecidas)
            total["inseridos"]  += res["inseridos"]
            total["duplicados"] += res["duplicados"]
            total["erros"]      += res["erros"]
            linhas_log.extend(res["detalhes"])

            log.code("\n".join(linhas_log[-30:]))

        barra.progress(1.0, text="Concluído!")

        db.inserir_import_log(
            arquivo=f"{len(arquivos)} arquivo(s)",
            inseridos=total["inseridos"],
            duplicados=total["duplicados"],
            erros=total["erros"],
            detalhes="\n".join(linhas_log))

        st.success(
            f"✅ Inseridos: **{total['inseridos']}**  |  "
            f"🔁 Duplicados: **{total['duplicados']}**  |  "
            f"❌ Erros: **{total['erros']}**")
