# =================================================================
# PAGES/PG_IMPORTACAO.PY
# =================================================================
import streamlit as st
import db
from etl_web import ProcessorETL
from theme_web import get_theme


def render():
    t = get_theme(st.session_state.get("tema", "Dark Emerald"))

    st.markdown(f"""
    <h2 style="color:{t['C_TEXT']}">📥 Importar Planilhas</h2>
    <p style="color:{t['C_MUTED']}">Faça upload de arquivos Excel (.xlsx / .xls)</p>
    <hr style="border-color:{t['C_BORDER']};"/>
    """, unsafe_allow_html=True)

    arquivos = st.file_uploader(
        "Selecione os arquivos Excel",
        type=["xlsx","xls"],
        accept_multiple_files=True,
        help="Arraste múltiplos arquivos de uma vez")

    if not arquivos:
        st.info("📂 Selecione um ou mais arquivos Excel para importar.")
        return

    st.markdown(f"**{len(arquivos)} arquivo(s) selecionado(s)**")

    if st.button("▶️  PROCESSAR ARQUIVOS", type="primary",
                  use_container_width=True):
        placas_conhecidas = set()
        df_veic = db.get_veiculos()
        if not df_veic.empty:
            placas_conhecidas = set(df_veic["placa"].tolist())

        total = {"inseridos": 0, "duplicados": 0, "erros": 0}
        barra = st.progress(0, text="Iniciando...")
        log   = st.empty()
        linhas_log = []

        for i, arq in enumerate(arquivos):
            barra.progress((i)/len(arquivos),
                           text=f"[{i+1}/{len(arquivos)}] {arq.name}...")
            linhas_log.append(f"\n▶ {arq.name}")
            log.code("\n".join(linhas_log[-20:]))

            res = ProcessorETL.process_uploaded_file(
                arq, arq.name, db, placas_conhecidas)
            total["inseridos"]  += res["inseridos"]
            total["duplicados"] += res["duplicados"]
            total["erros"]      += res["erros"]
            linhas_log.extend(res["detalhes"])
            log.code("\n".join(linhas_log[-20:]))

        barra.progress(1.0, text="✅ Concluído!")

        db.inserir_import_log(
            arquivo=f"{len(arquivos)} arquivo(s)",
            inseridos=total["inseridos"],
            duplicados=total["duplicados"],
            erros=total["erros"],
            detalhes="\n".join(linhas_log))

        c1, c2, c3 = st.columns(3)
        c1.metric("✅ Inseridos",  total["inseridos"])
        c2.metric("🔁 Duplicados", total["duplicados"])
        c3.metric("❌ Erros",      total["erros"])

        if total["inseridos"] > 0:
            st.success(f"✅ {total['inseridos']} registro(s) importado(s) com sucesso!")
            st.balloons()
        elif total["duplicados"] > 0:
            st.warning("Todos os registros já existiam no banco.")
        if total["erros"] > 0:
            st.error(f"{total['erros']} erro(s) durante a importação.")
