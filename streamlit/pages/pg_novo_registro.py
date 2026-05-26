# =================================================================
# PAGES/PG_NOVO_REGISTRO.PY
# =================================================================
import streamlit as st
from datetime import datetime
import db
from etl_web import identify_category
from theme_web import get_theme


def _parse_data(texto: str):
    """
    Aceita vários formatos e retorna (data_str AAAA-MM-DD, erro_str).
    Aceita: 25/05/2025, 25-05-2025, 25052025, 2025-05-25, 2025/05/25
    """
    texto = texto.strip().replace("-", "/").replace(".", "/")

    # Formato DDMMAAAA (sem separador, 8 dígitos)
    if texto.isdigit() and len(texto) == 8:
        texto = f"{texto[:2]}/{texto[2:4]}/{texto[4:]}"

    formatos = [
        ("%d/%m/%Y", True),   # 25/05/2025
        ("%Y/%m/%d", False),  # 2025/05/25
        ("%d/%m/%y", True),   # 25/05/25
    ]

    for fmt, _ in formatos:
        try:
            d = datetime.strptime(texto, fmt)
            return d.strftime("%Y-%m-%d"), d.strftime("%d/%m/%Y"), None
        except ValueError:
            continue

    return None, None, f"Data inválida: '{texto}'. Use DD/MM/AAAA"


def _formatar_auto(texto: str) -> str:
    """
    Autoformata enquanto o usuário digita:
    '2505'      → '25/05/'
    '250520'    → '25/05/20'
    '25052025'  → '25/05/2025'
    """
    # Remove tudo que não é dígito
    digits = "".join(c for c in texto if c.isdigit())

    if len(digits) <= 2:
        return digits
    elif len(digits) <= 4:
        return f"{digits[:2]}/{digits[2:]}"
    elif len(digits) <= 8:
        return f"{digits[:2]}/{digits[2:4]}/{digits[4:]}"
    else:
        return f"{digits[:2]}/{digits[2:4]}/{digits[4:8]}"


def render():
    t = get_theme(st.session_state.get("tema", "Dark Emerald"))

    st.markdown(f"""
    <h2 style="color:{t['C_TEXT']}">➕ Lançamento Manual</h2>
    <p style="color:{t['C_MUTED']}">Registre um abastecimento ou manutenção</p>
    <hr style="border-color:{t['C_BORDER']};"/>
    """, unsafe_allow_html=True)

    # CSS para feedback visual da data
    st.markdown("""
    <style>
    .data-ok    { color: #10B981; font-size: 12px; margin-top: 2px; }
    .data-erro  { color: #EF4444; font-size: 12px; margin-top: 2px; }
    .data-hint  { color: #64748B; font-size: 11px; margin-top: 2px; }
    </style>
    """, unsafe_allow_html=True)

    df_veic = db.get_veiculos()
    df_cond = db.get_condutores()
    veiculos   = df_veic["placa"].tolist() if not df_veic.empty else []
    condutores = df_cond["nome"].tolist()  if not df_cond.empty else []

    # Labels com modelo para facilitar identificação
    def label_v(placa):
        row = df_veic[df_veic["placa"] == placa]
        if not row.empty and row.iloc[0].get("modelo"):
            return f"{placa} — {row.iloc[0]['modelo']}"
        return placa

    labels_veic = [label_v(p) for p in veiculos]
    placa_map   = {label_v(p): p for p in veiculos}

    if not veiculos:
        st.warning("Cadastre ao menos um veículo antes de lançar.")
        return

    c1, c2 = st.columns(2)

    # ── Campo de data inteligente ─────────────────────────────────
    hoje_fmt = datetime.now().strftime("%d/%m/%Y")

    if "data_input" not in st.session_state:
        st.session_state["data_input"] = hoje_fmt

    with c1:
        st.markdown("**📅 Data** (DD/MM/AAAA)")
        data_raw = st.text_input(
            "data_input_lbl",
            value=st.session_state["data_input"],
            placeholder="DD/MM/AAAA",
            label_visibility="collapsed",
            key="data_txt",
            help="Digite a data no formato DD/MM/AAAA. Aceita também DD-MM-AAAA ou DDMMAAAA")

        # Autoformata e valida
        data_fmt_auto = _formatar_auto(data_raw)
        data_iso, data_exibicao, data_erro = _parse_data(data_raw)

        if data_iso:
            st.markdown(f'<p class="data-ok">✔ {data_exibicao}</p>',
                        unsafe_allow_html=True)
        elif data_raw and len(data_raw) > 2:
            st.markdown(f'<p class="data-erro">⚠ {data_erro or "Continue digitando..."}</p>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<p class="data-hint">Ex: 25/05/2025 ou 25-05-2025</p>',
                        unsafe_allow_html=True)

    with c2:
        sel_label = st.selectbox("🚛 Veículo (Placa)", labels_veic)
        placa     = placa_map.get(sel_label, veiculos[0] if veiculos else "")

    with c1:
        condutor = st.selectbox("👤 Condutor", condutores or ["—"])

    with c2:
        produto  = st.selectbox("⛽ Produto/Combustível",
                     ["DIESEL S10","DIESEL S500","GASOLINA","ETANOL",
                      "ARLA 32","ÓLEO","FILTRO","PNEU","OUTRO"])

    qtd   = c1.number_input("📦 Quantidade (L)",   min_value=0.0, step=0.1,  format="%.2f")
    valor = c1.number_input("💰 Valor Total (R$)", min_value=0.0, step=0.01, format="%.2f")
    hor   = c2.number_input("📏 Horímetro / KM",   min_value=0.0, step=1.0,  format="%.1f")

    categoria = identify_category(produto)
    st.info(f"Categoria detectada automaticamente: **{categoria}**")

    # ── Preço por litro ───────────────────────────────────────────
    if qtd > 0 and valor > 0:
        st.success(f"💡 Preço por litro: **R$ {valor/qtd:.3f}**")

    # ── Botão registrar ───────────────────────────────────────────
    if st.button("➕  FINALIZAR LANÇAMENTO", type="primary",
                  use_container_width=True):
        if not data_iso:
            st.error(f"⚠️ {data_erro or 'Data inválida. Use DD/MM/AAAA'}")
        elif qtd <= 0:
            st.error("⚠️ Informe a quantidade em litros.")
        elif valor <= 0:
            st.error("⚠️ Informe o valor total.")
        else:
            hv = f"MAN-{datetime.now().timestamp()}-{placa}"
            if db.inserir_registro(
                    data_iso, produto.upper(), condutor.upper(),
                    placa.upper(), "MANUAL", valor, qtd, hor,
                    categoria, "LANÇAMENTO MANUAL", hv):
                st.success(
                    f"✅ Registro salvo!\n\n"
                    f"📅 {data_exibicao}  |  🚛 {placa}  |  "
                    f"⛽ {produto}  |  📦 {qtd:.1f} L  |  💰 R$ {valor:.2f}")
                st.balloons()
                # Limpa a data para hoje
                st.session_state["data_input"] = hoje_fmt
                st.rerun()
            else:
                st.error("Erro ao salvar. Registro duplicado?")
