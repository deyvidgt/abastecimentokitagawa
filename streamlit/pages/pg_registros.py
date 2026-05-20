# =================================================================
# PAGES/PG_REGISTROS.PY
# =================================================================
import streamlit as st
import pandas as pd
from datetime import datetime
import db
from theme_web import get_theme
from export_utils import botoes_download


def render():
    t = get_theme(st.session_state.get("tema", "Dark Emerald"))

    st.markdown(f"""
    <h2 style="color:{t['C_TEXT']}">📋 Registros</h2>
    <p style="color:{t['C_MUTED']}">Pesquise, edite ou exclua lançamentos</p>
    <hr style="border-color:{t['C_BORDER']};"/>
    """, unsafe_allow_html=True)

    # ── Filtros ───────────────────────────────────────────────────
    c1,c2,c3,c4 = st.columns(4)
    placa_f   = c1.text_input("🔍 Placa / ID", placeholder="ex: ABC1234")
    produto_f = c2.text_input("Produto",        placeholder="ex: DIESEL")
    data_ini  = c3.date_input("De",  value=None)
    data_fim  = c4.date_input("Até", value=None)

    df = db.get_registros(
        data_ini=str(data_ini)    if data_ini   else None,
        data_fim=str(data_fim)    if data_fim   else None,
        placa=placa_f.upper()     if placa_f    else None,
        produto=produto_f.upper() if produto_f  else None)

    st.caption(f"{len(df)} registro(s) encontrado(s)")
    if df.empty:
        st.info("Nenhum registro encontrado."); return

    # ── Downloads ─────────────────────────────────────────────────
    df_exp = df[["id","data","placa","produto","responsavel",
                 "valor","quantidade","horimetro","categoria"]].copy()
    df_exp["data"] = df_exp["data"].astype(str)
    df_exp.columns = ["ID","Data","Placa","Produto","Condutor",
                      "Valor R$","Litros","Horímetro","Categoria"]

    botoes_download(st, df_exp, "registros",
        "REGISTROS — KITAGAWA",
        colunas_pdf=["Data","Placa","Produto","Valor R$","Litros","Categoria"],
        sheets_excel={"Registros": df_exp})

    # ── Tabela ────────────────────────────────────────────────────
    st.dataframe(df_exp, use_container_width=True, hide_index=True)

    st.divider()

    # ── Editar ────────────────────────────────────────────────────
    st.markdown("### ✏️ Editar Registro")
    st.caption("Digite o ID do registro que deseja editar:")
    reg_id = st.number_input("ID", min_value=1, step=1,
                              key="edit_id", label_visibility="collapsed")

    reg_row = df[df["id"] == reg_id]
    if not reg_row.empty:
        r = reg_row.iloc[0]
        veics = db.get_veiculos()
        conds = db.get_condutores()
        lv = veics["placa"].tolist() if not veics.empty else []
        lc = conds["nome"].tolist()  if not conds.empty else []

        with st.form("form_editar"):
            c1,c2,c3 = st.columns(3)
            nova_data  = c1.date_input("📅 Data",
                value=pd.to_datetime(r["data"]).date() if r["data"] else datetime.now().date())
            nova_placa = c2.selectbox("🚛 Placa", lv,
                index=lv.index(r["placa"]) if r["placa"] in lv else 0)
            nova_cat   = c3.selectbox("📁 Categoria",
                ["ABASTECIMENTO","MANUTENÇÃO"],
                index=0 if r["categoria"]=="ABASTECIMENTO" else 1)
            novo_prod  = c1.selectbox("⛽ Produto",
                ["DIESEL S10","DIESEL S500","GASOLINA","ETANOL",
                 "ARLA 32","ÓLEO","FILTRO","PNEU","OUTRO"])
            novo_cond  = c2.selectbox("👤 Condutor", lc or ["—"],
                index=lc.index(r["responsavel"]) if r["responsavel"] in lc else 0)
            novo_val   = c3.number_input("💰 Valor R$",
                value=float(r["valor"]), step=0.01, format="%.2f")
            nova_qtd   = c1.number_input("📦 Litros",
                value=float(r["quantidade"]), step=0.1, format="%.1f")
            novo_hor   = c2.number_input("📏 Horímetro",
                value=float(r["horimetro"]), step=1.0, format="%.0f")
            salvar = st.form_submit_button(
                "💾  SALVAR ALTERAÇÕES", use_container_width=True, type="primary")

        if salvar:
            if db.atualizar_registro(reg_id, str(nova_data), novo_prod,
                                      novo_cond, nova_placa, novo_val,
                                      nova_qtd, novo_hor, nova_cat):
                st.success(f"✅ Registro #{reg_id} atualizado!")
                st.rerun()
            else:
                st.error("Não foi possível salvar.")
    elif reg_id > 1:
        st.warning(f"Registro #{reg_id} não encontrado na busca atual.")

    st.divider()

    # ── Excluir ───────────────────────────────────────────────────
    st.markdown("### 🗑️ Excluir Registro")
    st.caption("⚠️ Esta ação não pode ser desfeita.")

    with st.form("form_excluir"):
        c1,c2 = st.columns([2,1])
        del_id = c1.number_input("ID a excluir", min_value=1, step=1,
                                   label_visibility="collapsed")
        confirmar = c2.form_submit_button(
            "🗑️  CONFIRMAR EXCLUSÃO", use_container_width=True, type="secondary")

    if confirmar:
        reg_del = df[df["id"] == del_id]
        if reg_del.empty:
            st.error(f"Registro #{del_id} não encontrado.")
        else:
            r = reg_del.iloc[0]
            st.warning(
                f"**Excluindo:** #{del_id} | {r['data']} | "
                f"{r['placa']} | {r['produto']} | R$ {r['valor']:.2f}")
            if db.excluir_registro(int(del_id)):
                st.success(f"✅ Registro #{del_id} excluído!")
                st.rerun()
            else:
                st.error("Não foi possível excluir.")
