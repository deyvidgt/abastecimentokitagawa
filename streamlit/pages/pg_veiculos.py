# =================================================================
# PAGES/PG_VEICULOS.PY
# =================================================================
import streamlit as st
import db
from theme_web import get_theme

TIPOS = ["Caminhão","Caminhonete","Trator","Van","Leve",
         "Máquina Agrícola","Drone","Outro"]
TIPOS_SEM_PLACA = {"Drone","Máquina Agrícola","Outro"}


def gerar_id(tipo):
    prefixo = {"Drone":"DRONE","Máquina Agrícola":"MAQ","Outro":"EQUIP"}.get(tipo,"ID")
    df = db.get_veiculos()
    nums = []
    if not df.empty:
        for p in df["placa"].dropna():
            if str(p).startswith(prefixo+"-"):
                try: nums.append(int(str(p).split("-")[-1]))
                except ValueError: pass
    return f"{prefixo}-{max(nums, default=0)+1:03d}"


def render():
    t = get_theme(st.session_state.get("tema", "Dark Emerald"))

    st.markdown(f"""
    <h2 style="color:{t['C_TEXT']}">🚗 Cadastro de Veículos</h2>
    <hr style="border-color:{t['C_BORDER']};"/>
    """, unsafe_allow_html=True)

    with st.expander("➕ Novo veículo / equipamento", expanded=True):
        c1, c2, c3, c4 = st.columns([2, 2, 1.5, 1])
        tipo   = c1.selectbox("Tipo", TIPOS, key="tipo_novo")
        sem    = tipo in TIPOS_SEM_PLACA
        label  = "Identificador" if sem else "Placa"
        placa  = c2.text_input(label,
                    placeholder="ex: DRONE-001" if sem else "ex: ABC1234",
                    key="placa_novo")
        modelo = c3.text_input("Modelo / Descrição", key="modelo_novo")

        col_btn1, col_btn2 = c4.columns(2)
        with col_btn1:
            if sem and st.button("🔢 Gerar ID", key="gerar_id_btn"):
                st.session_state["id_gerado"] = gerar_id(tipo)
        if "id_gerado" in st.session_state and sem:
            st.info(f"ID sugerido: **{st.session_state['id_gerado']}**")

        if st.button("💾 Cadastrar", type="primary", key="cad_btn"):
            p = (st.session_state.get("id_gerado","") or placa).upper().strip()
            m = modelo.upper().strip()
            if not p or not m:
                st.warning(f"{label} e Modelo são obrigatórios.")
            elif db.inserir_veiculo(p, m, tipo):
                st.success(f"✅ {label} {p} cadastrado!")
                if "id_gerado" in st.session_state:
                    del st.session_state["id_gerado"]
                st.rerun()
            else:
                st.error(f"{label} já existe.")

    st.divider()

    df = db.get_veiculos()
    if df.empty:
        st.info("Nenhum veículo cadastrado.")
        return

    st.dataframe(df[["placa","modelo","tipo","status"]],
                 use_container_width=True, hide_index=True)

    col_edit, col_del = st.columns(2)

    with col_edit:
        with st.expander("✏️ Editar veículo"):
            placas = df["placa"].tolist()
            sel    = st.selectbox("Selecione", placas, key="sel_edit")
            row    = df[df["placa"]==sel].iloc[0]
            c1, c2 = st.columns(2)
            nova_placa  = c1.text_input("Nova placa", value=row["placa"], key="np")
            novo_modelo = c1.text_input("Modelo",     value=row["modelo"] or "", key="nm")
            novo_tipo   = c2.selectbox("Tipo", TIPOS, key="nt",
                            index=TIPOS.index(row["tipo"])
                                  if row["tipo"] in TIPOS else 0)
            novo_status = c2.selectbox("Status",
                            ["Ativo","Inativo","Manutenção"], key="ns",
                            index=["Ativo","Inativo","Manutenção"].index(row["status"])
                                  if row["status"] in ["Ativo","Inativo","Manutenção"] else 0)
            if st.button("💾 Salvar", type="primary", key="salvar_veic"):
                if db.atualizar_veiculo(sel, nova_placa.upper(),
                                         novo_modelo.upper(), novo_tipo, novo_status):
                    st.success("Veículo atualizado!")
                    st.rerun()
                else:
                    st.error("Não foi possível salvar.")

    with col_del:
        with st.expander("🗑️ Excluir veículo"):
            sel_del = st.selectbox("Placa a excluir",
                                    df["placa"].tolist(), key="del_veic")
            st.caption("Os registros de abastecimento não serão apagados.")
            if st.button("🗑️ Excluir", type="secondary", key="del_veic_btn"):
                if db.excluir_veiculo(sel_del):
                    st.success(f"{sel_del} removido.")
                    st.rerun()
                else:
                    st.error("Não foi possível excluir.")
