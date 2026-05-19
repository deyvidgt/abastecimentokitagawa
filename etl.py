# =================================================================
# ETL.PY — Motor de importação / transformação de planilhas
# =================================================================
import os
import re
import logging
import difflib
from datetime import datetime

import pandas as pd

# ── Mapeamento de colunas ─────────────────────────────────────────
COLUMN_ALIASES = {
    "DATA":        ["data","dt","date","dat","data lançamento","data abas",
                    "data do lançamento","data abastecimento","data_abas",
                    "emissao","emissão"],
    "PRODUTO":     ["produto","combustivel","combustível","descricao","descrição",
                    "item","tipo combustivel","tipo de combustível","material"],
    "RESPONSAVEL": ["responsavel","responsável","motorista","condutor","driver",
                    "operador","nome","usuario","usuário","solicitante"],
    "PLACA":       ["placa","veiculo","veículo","placa veiculo","placa do veiculo",
                    "identificacao","identificação","tag","placa/frota"],
    "FROTA":       ["frota","nº frota","n frota","num frota","numero frota",
                    "nro frota","codigo frota","cod frota","fleet"],
    "VALOR":       ["valor","total","custo","r$","preco","preço","valor total",
                    "valor pago","custo total","vlr","vl total"],
    "QUANTIDADE":  ["quantidade","qtd","litros","volume","lts","qt",
                    "quantidade lt","quantidade lts","litros abastecidos","qty"],
    "HORIMETRO":   ["horimetro","horímetro","km","quilometragem","odometro",
                    "odômetro","hodometro","km atual","km rodados","hora"],
}

DATE_FORMATS = [
    "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d",
    "%d/%m/%y", "%m/%d/%Y", "%Y%m%d",  "%d.%m.%Y",
]

MANUTENCAO_KW = [
    'OLEO','FILTRO','LUBRIFICANTE','PECA','PEÇA','PNEU',
    'REVISAO','REVISÃO','ARLA','STP','LAVAGEM','BORRACHA',
    'CORREIA','BATERIA','FREIO',
]


class ProcessorETL:

    # ── Limpeza de dados ──────────────────────────────────────────
    @staticmethod
    def clean_numeric(value):
        if pd.isna(value) or str(value).strip() in ("", "-", "N/A", "n/a"):
            return 0.0
        s = re.sub(r"[R$\s]", "", str(value).strip())
        if "," in s and "." in s:
            s = (s.replace(".", "").replace(",", ".")
                 if s.rfind(",") > s.rfind(".") else s.replace(",", ""))
        elif "," in s:
            s = s.replace(",", ".")
        try:
            return float(s)
        except Exception:
            return 0.0

    @staticmethod
    def parse_date(value):
        if pd.isna(value):
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, pd.Timestamp):
            return value.to_pydatetime()
        s = str(value).strip()
        for fmt in DATE_FORMATS:
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                pass
        try:
            return pd.to_datetime(s, dayfirst=True).to_pydatetime()
        except Exception:
            return None

    @staticmethod
    def identify_category(product_name):
        return ("MANUTENÇÃO"
                if any(k in str(product_name).upper() for k in MANUTENCAO_KW)
                else "ABASTECIMENTO")

    # ── Detecção de colunas ───────────────────────────────────────
    @classmethod
    def detect_columns(cls, raw_cols):
        mapping = {}
        raw_lower = [str(c).lower().strip() for c in raw_cols]
        for canonical, aliases in COLUMN_ALIASES.items():
            best_score, best_raw = 0.0, None
            for rl, ro in zip(raw_lower, raw_cols):
                if rl in aliases:
                    best_raw = ro
                    best_score = 1.0
                    break
                m = difflib.get_close_matches(rl, aliases, n=1, cutoff=0.60)
                if m:
                    sc = difflib.SequenceMatcher(None, rl, m[0]).ratio()
                    if sc > best_score:
                        best_score = sc
                        best_raw = ro
            if best_raw:
                mapping[canonical] = best_raw
        return mapping

    @classmethod
    def find_header_row(cls, df_raw):
        all_aliases = [a for v in COLUMN_ALIASES.values() for a in v]
        best_row, best_hits = 0, 0
        for i, row in df_raw.head(20).iterrows():
            hits = sum(
                1 for cell in row
                if difflib.get_close_matches(
                    str(cell).lower().strip(), all_aliases, n=1, cutoff=0.70)
            )
            if hits > best_hits:
                best_hits = hits
                best_row = i
        return best_row if best_hits >= 2 else 0

    # ── Scanner de placas novas ───────────────────────────────────
    @classmethod
    def scan_new_plates(cls, file_path, known_plates):
        new_plates = set()
        try:
            all_sheets = pd.read_excel(
                file_path, sheet_name=None, header=None, dtype=str)
            for _, df_raw in all_sheets.items():
                if df_raw.empty:
                    continue
                hr     = cls.find_header_row(df_raw)
                header = df_raw.iloc[hr].tolist()
                df     = df_raw.iloc[hr + 1:].copy()
                df.columns = header
                col_map = cls.detect_columns(df.columns.tolist())
                if "PLACA" not in col_map:
                    continue
                for v in df[col_map["PLACA"]].dropna().unique():
                    p = str(v).upper().strip()[:20]
                    if p and p not in known_plates and p not in ("NAN", "NONE", ""):
                        new_plates.add(p)
        except Exception as e:
            logging.error(f"scan_new_plates: {e}")
        return new_plates

    # ── Inserção individual com diagnóstico preciso ───────────────
    @staticmethod
    def _insert_registro(db_engine, params):
        """
        BUG FIX: antes o ETL usava execute_query() que retorna False para
        AMBOS os casos — IntegrityError (duplicata legítima) e qualquer
        outra exceção (erro real de banco). Isso fazia com que erros reais
        fossem contados como 'duplicados', escondendo problemas do usuário.

        Esta função separa os dois casos:
          - "ok"        → linha inserida com sucesso
          - "duplicate" → hash já existe (duplicata esperada)
          - "error"     → falha inesperada (logar e contar como erro)
        """
        import sqlite3
        with db_engine._lock:
            try:
                db_engine.cursor.execute("""
                    INSERT OR IGNORE INTO registros
                    (data,produto,responsavel,placa,frota,valor,quantidade,
                     horimetro,categoria,arquivo_origem,hash_verificacao)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)
                """, params)
                db_engine.conn.commit()
                # rowcount == 0 significa que o INSERT foi ignorado (UNIQUE hit)
                return "ok" if db_engine.cursor.rowcount > 0 else "duplicate"
            except sqlite3.IntegrityError:
                return "duplicate"
            except Exception as e:
                logging.error(f"_insert_registro: {e}")
                return "error"

    # ── Processamento de arquivo Excel ────────────────────────────
    @classmethod
    def process_excel(cls, file_path, db_engine):
        filename = os.path.basename(file_path)
        stats = {"inseridos": 0, "duplicados": 0, "erros": 0, "detalhes": []}
        try:
            all_sheets = pd.read_excel(
                file_path, sheet_name=None, header=None, dtype=str)
        except Exception as e:
            stats["detalhes"].append(f"[ERRO FATAL] {filename}: {e}")
            stats["erros"] += 1
            return stats

        for sheet_name, df_raw in all_sheets.items():
            if df_raw.empty:
                continue
            hr     = cls.find_header_row(df_raw)
            header = df_raw.iloc[hr].tolist()
            df     = df_raw.iloc[hr + 1:].copy()
            df.columns = header
            df     = df.reset_index(drop=True)
            df.dropna(how="all", inplace=True)
            df = df[~df.apply(
                lambda r: all(str(v).strip() in ("", "nan", "None") for v in r),
                axis=1)]

            col_map = cls.detect_columns(df.columns.tolist())
            if "DATA" not in col_map or "VALOR" not in col_map:
                stats["detalhes"].append(
                    f"[SKIP] '{sheet_name}': DATA/VALOR não detectados")
                continue
            stats["detalhes"].append(
                f"[OK] '{sheet_name}' → header linha {hr+1}, mapeado: {col_map}")

            for _, row in df.iterrows():
                dv = cls.parse_date(row.get(col_map.get("DATA")))
                vl = cls.clean_numeric(row.get(col_map.get("VALOR", ""), 0))
                if dv is None or vl == 0:
                    continue

                placa   = str(row.get(col_map.get("PLACA", ""),
                              filename.split(".")[0])).upper().strip()[:20]
                produto = str(row.get(col_map.get("PRODUTO", ""),
                              "DESCONHECIDO")).upper().strip()
                resp    = str(row.get(col_map.get("RESPONSAVEL", ""),
                              "S/I")).upper().strip()
                frota   = str(row.get(col_map.get("FROTA", ""),
                              "S/F")).upper().strip()
                qtd     = cls.clean_numeric(
                    row.get(col_map.get("QUANTIDADE", ""), 0))
                hor     = cls.clean_numeric(
                    row.get(col_map.get("HORIMETRO", ""), 0))
                hv      = (f"{dv.strftime('%Y%m%d')}-{placa}"
                           f"-{vl:.2f}-{hor:.1f}-{qtd:.2f}")

                # BUG FIX: usar _insert_registro para distinguir duplicata de erro real
                resultado = cls._insert_registro(db_engine, (
                    dv.strftime("%Y-%m-%d"), produto, resp, placa, frota,
                    vl, qtd, hor,
                    cls.identify_category(produto), filename, hv))

                if resultado == "ok":
                    stats["inseridos"] += 1
                elif resultado == "duplicate":
                    stats["duplicados"] += 1
                else:  # "error" — antes contado erroneamente como duplicado
                    stats["erros"] += 1
                    stats["detalhes"].append(
                        f"  [ERRO INSERT] {dv.date()} | {placa} | R${vl:.2f}")

        db_engine.execute_query("""
            INSERT INTO import_log
            (arquivo,data_import,inseridos,duplicados,erros,detalhes)
            VALUES (?,?,?,?,?,?)
        """, (filename, datetime.now().isoformat(),
              stats["inseridos"], stats["duplicados"], stats["erros"],
              "\n".join(stats["detalhes"])))
        return stats
