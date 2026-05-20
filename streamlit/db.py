# =================================================================
# DB.PY — Camada de acesso ao Supabase
# =================================================================
import hashlib
import streamlit as st
from supabase import create_client, Client
import pandas as pd


def _hash(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()


@st.cache_resource
def get_client() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)


# ── Autenticação ──────────────────────────────────────────────────
def verificar_login(usuario: str, senha: str) -> dict | None:
    sb = get_client()
    res = sb.table("usuarios").select("*").eq(
        "usuario", usuario.strip()).eq("ativo", True).execute()
    if not res.data: return None
    u = res.data[0]
    return u if u["senha_hash"] == _hash(senha) else None


def alterar_senha(usuario: str, nova_senha: str) -> bool:
    sb = get_client()
    res = sb.table("usuarios").update(
        {"senha_hash": _hash(nova_senha)}
    ).eq("usuario", usuario.strip()).execute()
    return bool(res.data)


def listar_usuarios() -> pd.DataFrame:
    sb = get_client()
    res = sb.table("usuarios").select(
        "id,usuario,perfil,ativo,criado_em").order("usuario").execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()


def criar_usuario(usuario: str, senha: str, perfil: str = "operador") -> bool:
    sb = get_client()
    try:
        sb.table("usuarios").insert({
            "usuario":    usuario.strip(),
            "senha_hash": _hash(senha),
            "perfil":     perfil,
            "ativo":      True,
        }).execute()
        return True
    except Exception:
        return False


# ── Preferências por usuário ──────────────────────────────────────
def salvar_preferencia_usuario(usuario: str, chave: str, valor: str):
    """Salva preferência do usuário (ex: tema) no Supabase."""
    sb = get_client()
    try:
        # Verifica se já existe
        res = sb.table("preferencias_usuario").select("id").eq(
            "usuario", usuario).eq("chave", chave).execute()
        if res.data:
            sb.table("preferencias_usuario").update(
                {"valor": valor}
            ).eq("usuario", usuario).eq("chave", chave).execute()
        else:
            sb.table("preferencias_usuario").insert({
                "usuario": usuario, "chave": chave, "valor": valor
            }).execute()
    except Exception:
        pass  # Falha silenciosa


def get_preferencia_usuario(usuario: str, chave: str,
                              default: str = None) -> str | None:
    """Busca preferência do usuário no Supabase."""
    sb = get_client()
    try:
        res = sb.table("preferencias_usuario").select("valor").eq(
            "usuario", usuario).eq("chave", chave).execute()
        if res.data:
            return res.data[0]["valor"]
    except Exception:
        pass
    return default


# ── Veículos ──────────────────────────────────────────────────────
def get_veiculos() -> pd.DataFrame:
    sb = get_client()
    res = sb.table("veiculos").select("*").order("placa").execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()


def inserir_veiculo(placa, modelo, tipo, status="Ativo") -> bool:
    sb = get_client()
    try:
        sb.table("veiculos").insert({
            "placa": placa.upper().strip(),
            "modelo": modelo.upper().strip(),
            "tipo": tipo, "status": status,
        }).execute()
        return True
    except Exception:
        return False


def atualizar_veiculo(placa_antiga, placa_nova, modelo, tipo, status) -> bool:
    sb = get_client()
    try:
        sb.table("registros").update(
            {"placa": placa_nova}).eq("placa", placa_antiga).execute()
        sb.table("veiculos").update({
            "placa": placa_nova, "modelo": modelo,
            "tipo": tipo, "status": status,
        }).eq("placa", placa_antiga).execute()
        return True
    except Exception:
        return False


def excluir_veiculo(placa: str) -> bool:
    sb = get_client()
    try:
        sb.table("veiculos").delete().eq("placa", placa).execute()
        return True
    except Exception:
        return False


# ── Condutores ────────────────────────────────────────────────────
def get_condutores() -> pd.DataFrame:
    sb = get_client()
    res = sb.table("condutores").select("*").order("nome").execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()


def inserir_condutor(nome: str) -> bool:
    sb = get_client()
    try:
        sb.table("condutores").insert({"nome": nome.upper().strip()}).execute()
        return True
    except Exception:
        return False


# ── Registros ─────────────────────────────────────────────────────
def get_registros(data_ini=None, data_fim=None,
                  placa=None, produto=None, limit=500) -> pd.DataFrame:
    sb = get_client()
    q  = sb.table("registros").select("*")
    if data_ini: q = q.gte("data", data_ini)
    if data_fim: q = q.lte("data", data_fim)
    if placa:    q = q.ilike("placa", f"%{placa}%")
    if produto:  q = q.ilike("produto", f"%{produto}%")
    res = q.order("data", desc=True).limit(limit).execute()
    if not res.data: return pd.DataFrame()
    df = pd.DataFrame(res.data)
    for col in ["valor","quantidade","horimetro"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    return df


def get_todos_registros() -> pd.DataFrame:
    return get_registros(limit=10000)


def inserir_registro(data, produto, responsavel, placa, frota,
                     valor, quantidade, horimetro,
                     categoria, arquivo_origem, hash_v) -> bool:
    sb = get_client()
    try:
        sb.table("registros").insert({
            "data": data, "produto": produto, "responsavel": responsavel,
            "placa": placa, "frota": frota, "valor": valor,
            "quantidade": quantidade, "horimetro": horimetro,
            "categoria": categoria, "arquivo_origem": arquivo_origem,
            "hash_verificacao": hash_v,
        }).execute()
        return True
    except Exception:
        return False


def atualizar_registro(reg_id, data, produto, responsavel, placa,
                        valor, quantidade, horimetro, categoria) -> bool:
    hv = f"{data}-{placa}-{valor:.2f}-{horimetro:.1f}-{quantidade:.2f}-EDIT{reg_id}"
    sb = get_client()
    try:
        sb.table("registros").update({
            "data": data, "produto": produto, "responsavel": responsavel,
            "placa": placa, "valor": valor, "quantidade": quantidade,
            "horimetro": horimetro, "categoria": categoria,
            "hash_verificacao": hv,
        }).eq("id", reg_id).execute()
        return True
    except Exception:
        return False


def excluir_registro(reg_id: int) -> bool:
    sb = get_client()
    try:
        sb.table("registros").delete().eq("id", reg_id).execute()
        return True
    except Exception:
        return False


# ── Import log ────────────────────────────────────────────────────
def get_import_log() -> pd.DataFrame:
    sb = get_client()
    res = sb.table("import_log").select("*").order(
        "id", desc=True).limit(60).execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()


def inserir_import_log(arquivo, inseridos, duplicados, erros, detalhes):
    sb = get_client()
    from datetime import datetime
    sb.table("import_log").insert({
        "arquivo": arquivo,
        "data_import": datetime.now().isoformat(),
        "inseridos": inseridos, "duplicados": duplicados,
        "erros": erros, "detalhes": detalhes,
    }).execute()
