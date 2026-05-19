# =================================================================
# DATABASE.PY — Camada de acesso ao banco de dados (SQLite)
# =================================================================
import sqlite3
import hashlib
import logging
import threading
import pandas as pd
from config import DB_NAME


def _hash_senha(senha: str) -> str:
    """SHA-256 da senha. Nunca armazena senha em texto puro."""
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


class DataEngine:
    def __init__(self):
        self._lock  = threading.Lock()
        self.conn   = sqlite3.connect(DB_NAME, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._initialize_schema()

    # ── Schema ────────────────────────────────────────────────────
    def _initialize_schema(self):
        ddl_list = [
            """CREATE TABLE IF NOT EXISTS veiculos (
                placa TEXT PRIMARY KEY, modelo TEXT, tipo TEXT,
                combustivel TEXT, horimetro_atual REAL DEFAULT 0,
                status TEXT DEFAULT 'Ativo')""",
            """CREATE TABLE IF NOT EXISTS condutores (
                nome TEXT PRIMARY KEY, data_cadastro DATE)""",
            """CREATE TABLE IF NOT EXISTS registros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data DATE, produto TEXT, responsavel TEXT,
                placa TEXT, frota TEXT, valor REAL,
                quantidade REAL, horimetro REAL, categoria TEXT,
                arquivo_origem TEXT, hash_verificacao TEXT UNIQUE,
                FOREIGN KEY (placa) REFERENCES veiculos(placa))""",
            """CREATE TABLE IF NOT EXISTS import_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                arquivo TEXT, data_import DATETIME,
                inseridos INTEGER, duplicados INTEGER,
                erros INTEGER, detalhes TEXT)""",
            """CREATE TABLE IF NOT EXISTS configuracoes (
                chave TEXT PRIMARY KEY, valor TEXT)""",
            # ── Tabela de usuários (NOVO) ──────────────────────────
            """CREATE TABLE IF NOT EXISTS usuarios (
                id        INTEGER  PRIMARY KEY AUTOINCREMENT,
                usuario   TEXT     NOT NULL UNIQUE,
                senha_hash TEXT    NOT NULL,
                perfil    TEXT     NOT NULL DEFAULT 'operador',
                ativo     INTEGER  NOT NULL DEFAULT 1,
                criado_em DATETIME DEFAULT CURRENT_TIMESTAMP)""",
        ]
        for q in ddl_list:
            self.cursor.execute(q)
        self.conn.commit()

        # Cria usuário admin padrão se tabela estiver vazia
        self.cursor.execute("SELECT COUNT(*) FROM usuarios")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute(
                "INSERT INTO usuarios (usuario, senha_hash, perfil) VALUES (?,?,?)",
                ("admin", _hash_senha("admin123"), "admin"))
            self.conn.commit()
            logging.info(
                "Usuário padrão criado → usuario: admin | senha: admin123\n"
                "Troque a senha no primeiro acesso!")

    # ── CRUD genérico ─────────────────────────────────────────────
    def execute_query(self, query, params=()):
        with self._lock:
            try:
                self.cursor.execute(query, params)
                self.conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False
            except Exception as e:
                logging.error(f"DB: {e}")
                return False

    def get_dataframe(self, sql, params=()):
        with self._lock:
            return pd.read_sql_query(sql, self.conn, params=params)

    # ── Helpers específicos ───────────────────────────────────────
    def placas_cadastradas(self):
        return set(self.get_dataframe(
            "SELECT placa FROM veiculos")["placa"].tolist())

    def get_config(self, chave, default=""):
        try:
            with self._lock:
                self.cursor.execute(
                    "SELECT valor FROM configuracoes WHERE chave=?", (chave,))
                row = self.cursor.fetchone()
            return row[0] if row else default
        except Exception:
            return default

    def set_config(self, chave, valor):
        self.execute_query(
            "INSERT OR REPLACE INTO configuracoes (chave,valor) VALUES (?,?)",
            (chave, valor))

    # ── AUTENTICAÇÃO ──────────────────────────────────────────────
    def verificar_login(self, usuario: str, senha: str) -> bool:
        """Retorna True se usuário e senha corretos e conta ativa."""
        with self._lock:
            self.cursor.execute(
                "SELECT senha_hash, ativo FROM usuarios WHERE usuario=?",
                (usuario.strip(),))
            row = self.cursor.fetchone()
        if not row:
            return False
        senha_hash, ativo = row
        return ativo == 1 and senha_hash == _hash_senha(senha)

    def alterar_senha(self, usuario: str, nova_senha: str) -> bool:
        """Troca a senha de um usuário. Retorna False se não existir."""
        with self._lock:
            self.cursor.execute(
                "SELECT id FROM usuarios WHERE usuario=?", (usuario.strip(),))
            if not self.cursor.fetchone():
                return False
            self.cursor.execute(
                "UPDATE usuarios SET senha_hash=? WHERE usuario=?",
                (_hash_senha(nova_senha), usuario.strip()))
            self.conn.commit()
        return True

    def criar_usuario(self, usuario: str, senha: str,
                      perfil: str = "operador") -> bool:
        """Cria novo usuário. Retorna False se já existir."""
        return self.execute_query(
            "INSERT INTO usuarios (usuario, senha_hash, perfil) VALUES (?,?,?)",
            (usuario.strip(), _hash_senha(senha), perfil))

    def listar_usuarios(self):
        """DataFrame de usuários sem expor senha_hash."""
        return self.get_dataframe(
            "SELECT id, usuario, perfil, ativo, criado_em "
            "FROM usuarios ORDER BY usuario")

    # ── Registros ─────────────────────────────────────────────────
    def get_registro_by_id(self, reg_id):
        with self._lock:
            self.cursor.execute("SELECT * FROM registros WHERE id=?", (reg_id,))
            row = self.cursor.fetchone()
            if not row:
                return None
            return dict(zip([d[0] for d in self.cursor.description], row))

    def update_registro(self, reg_id, data, produto, responsavel, placa,
                        valor, quantidade, horimetro, categoria):
        hv = (f"{data}-{placa}-{valor:.2f}"
              f"-{horimetro:.1f}-{quantidade:.2f}-EDIT{reg_id}")
        return self.execute_query("""
            UPDATE registros
            SET data=?,produto=?,responsavel=?,placa=?,
                valor=?,quantidade=?,horimetro=?,
                categoria=?,hash_verificacao=?
            WHERE id=?""",
            (data, produto, responsavel, placa,
             valor, quantidade, horimetro, categoria, hv, reg_id))

    def delete_registro(self, reg_id):
        return self.execute_query(
            "DELETE FROM registros WHERE id=?", (reg_id,))

    # ── Veículos ──────────────────────────────────────────────────
    def update_veiculo(self, placa_antiga, placa_nova, modelo, tipo, status):
        with self._lock:
            try:
                self.cursor.execute(
                    "UPDATE registros SET placa=? WHERE placa=?",
                    (placa_nova, placa_antiga))
                self.cursor.execute(
                    "UPDATE veiculos SET placa=?,modelo=?,tipo=?,status=? WHERE placa=?",
                    (placa_nova, modelo, tipo, status, placa_antiga))
                self.conn.commit()
                return True
            except Exception as e:
                logging.error(f"update_veiculo: {e}")
                self.conn.rollback()
                return False

    def delete_veiculo(self, placa):
        return self.execute_query(
            "DELETE FROM veiculos WHERE placa=?", (placa,))
