-- =================================================================
-- SUPABASE_SCHEMA.SQL
-- Execute no SQL Editor do Supabase (apenas uma vez)
-- =================================================================

CREATE TABLE IF NOT EXISTS usuarios (
    id         SERIAL PRIMARY KEY,
    usuario    TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    perfil     TEXT NOT NULL DEFAULT 'operador',
    ativo      BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em  TIMESTAMP DEFAULT NOW()
);

-- Usuário admin padrão (senha: admin123)
INSERT INTO usuarios (usuario, senha_hash, perfil)
VALUES (
    'admin',
    '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9',
    'admin'
) ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS veiculos (
    placa           TEXT PRIMARY KEY,
    modelo          TEXT,
    tipo            TEXT,
    combustivel     TEXT,
    horimetro_atual REAL DEFAULT 0,
    status          TEXT DEFAULT 'Ativo'
);

CREATE TABLE IF NOT EXISTS condutores (
    nome        TEXT PRIMARY KEY,
    data_cadastro DATE DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS registros (
    id               SERIAL PRIMARY KEY,
    data             DATE,
    produto          TEXT,
    responsavel      TEXT,
    placa            TEXT,
    frota            TEXT,
    valor            REAL,
    quantidade       REAL,
    horimetro        REAL,
    categoria        TEXT,
    arquivo_origem   TEXT,
    hash_verificacao TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS import_log (
    id          SERIAL PRIMARY KEY,
    arquivo     TEXT,
    data_import TIMESTAMP DEFAULT NOW(),
    inseridos   INTEGER,
    duplicados  INTEGER,
    erros       INTEGER,
    detalhes    TEXT
);
