# =================================================================
# ETL_WEB.PY — Motor ETL adaptado para Streamlit
# Processa st.UploadedFile em vez de caminhos de disco
# =================================================================
import re
import logging
import difflib
from datetime import datetime
import pandas as pd

COLUMN_ALIASES = {
    "DATA":        ["data","dt","date","dat","data lançamento","data abas",
                    "data do lançamento","data abastecimento","emissao","emissão"],
    "PRODUTO":     ["produto","combustivel","combustível","descricao","descrição",
                    "item","tipo combustivel","material"],
    "RESPONSAVEL": ["responsavel","responsável","motorista","condutor","driver",
                    "operador","nome","usuario","solicitante"],
    "PLACA":       ["placa","veiculo","veículo","placa veiculo","placa do veiculo",
                    "identificacao","identificação","tag","placa/frota"],
    "FROTA":       ["frota","nº frota","n frota","num frota","numero frota","fleet"],
    "VALOR":       ["valor","total","custo","r$","preco","preço","valor total",
                    "valor pago","custo total","vlr"],
    "QUANTIDADE":  ["quantidade","qtd","litros","volume","lts","qt",
                    "litros abastecidos","qty"],
    "HORIMETRO":   ["horimetro","horímetro","km","quilometragem","odometro",
                    "odômetro","hodometro","km atual","hora"],
}

DATE_FORMATS = ["%Y-%m-%d","%d/%m/%Y","%d-%m-%Y","%Y/%m/%d",
                "%d/%m/%y","%m/%d/%Y","%Y%m%d","%d.%m.%Y"]

MANUTENCAO_KW = ["OLEO","FILTRO","LUBRIFICANTE","PECA","PEÇA","PNEU",
                  "REVISAO","REVISÃO","ARLA","STP","LAVAGEM","BORRACHA",
                  "CORREIA","BATERIA","FREIO"]


def identify_category(product_name: str) -> str:
    return ("MANUTENÇÃO"
            if any(k in str(product_name).upper() for k in MANUTENCAO_KW)
            else "ABASTECIMENTO")


class ProcessorETL:

    @staticmethod
    def clean_numeric(value):
        if pd.isna(value) or str(value).strip() in ("","-","N/A","n/a"):
            return 0.0
        s = re.sub(r"[R$\s]", "", str(value).strip())
        if "," in s and "." in s:
            s = (s.replace(".","").replace(",",".")
                 if s.rfind(",") > s.rfind(".") else s.replace(",",""))
        elif "," in s:
            s = s.replace(",",".")
        try:    return float(s)
        except: return 0.0

    @staticmethod
    def parse_date(value):
        if pd.isna(value): return None
        if isinstance(value, datetime): return value
        if isinstance(value, pd.Timestamp): return value.to_pydatetime()
        s = str(value).strip()
        for fmt in DATE_FORMATS:
            try: return datetime.strptime(s, fmt)
            except ValueError: pass
        try:    return pd.to_datetime(s, dayfirst=True).to_pydatetime()
        except: return None

    @classmethod
    def detect_columns(cls, raw_cols):
        mapping, raw_lower = {}, [str(c).lower().strip() for c in raw_cols]
        for canonical, aliases in COLUMN_ALIASES.items():
            best_score, best_raw = 0.0, None
            for rl, ro in zip(raw_lower, raw_cols):
                if rl in aliases:
                    best_raw, best_score = ro, 1.0; break
                m = difflib.get_close_matches(rl, aliases, n=1, cutoff=0.60)
                if m:
                    sc = difflib.SequenceMatcher(None, rl, m[0]).ratio()
                    if sc > best_score:
                        best_score, best_raw = sc, ro
            if best_raw: mapping[canonical] = best_raw
        return mapping

    @classmethod
    def find_header_row(cls, df_raw):
        all_aliases = [a for v in COLUMN_ALIASES.values() for a in v]
        best_row, best_hits = 0, 0
        for i, row in df_raw.head(20).iterrows():
            hits = sum(1 for cell in row if difflib.get_close_matches(
                str(cell).lower().strip(), all_aliases, n=1, cutoff=0.70))
            if hits > best_hits:
                best_hits, best_row = hits, i
        return best_row if best_hits >= 2 else 0

    @classmethod
    def process_uploaded_file(cls, uploaded_file, filename, db_engine,
                               placas_conhecidas=None) -> dict:
        stats = {"inseridos": 0, "duplicados": 0, "erros": 0, "detalhes": []}
        try:
            all_sheets = pd.read_excel(
                uploaded_file, sheet_name=None, header=None, dtype=str)
        except Exception as e:
            stats["detalhes"].append(f"[ERRO FATAL] {filename}: {e}")
            stats["erros"] += 1
            return stats

        for sheet_name, df_raw in all_sheets.items():
            if df_raw.empty: continue
            hr     = cls.find_header_row(df_raw)
            header = df_raw.iloc[hr].tolist()
            df     = df_raw.iloc[hr+1:].copy()
            df.columns = header
            df     = df.reset_index(drop=True)
            df.dropna(how="all", inplace=True)
            col_map = cls.detect_columns(df.columns.tolist())

            if "DATA" not in col_map or "VALOR" not in col_map:
                stats["detalhes"].append(f"[SKIP] '{sheet_name}': DATA/VALOR não detectados")
                continue
            stats["detalhes"].append(f"[OK] '{sheet_name}' → mapeado: {col_map}")

            for _, row in df.iterrows():
                dv = cls.parse_date(row.get(col_map.get("DATA")))
                vl = cls.clean_numeric(row.get(col_map.get("VALOR",""), 0))
                if dv is None or vl == 0: continue

                placa   = str(row.get(col_map.get("PLACA",""),
                              filename.split(".")[0])).upper().strip()[:20]
                produto = str(row.get(col_map.get("PRODUTO",""),
                              "DESCONHECIDO")).upper().strip()
                resp    = str(row.get(col_map.get("RESPONSAVEL",""),"S/I")).upper().strip()
                frota   = str(row.get(col_map.get("FROTA",""),"S/F")).upper().strip()
                qtd     = cls.clean_numeric(row.get(col_map.get("QUANTIDADE",""), 0))
                hor     = cls.clean_numeric(row.get(col_map.get("HORIMETRO",""), 0))
                hv      = f"{dv.strftime('%Y%m%d')}-{placa}-{vl:.2f}-{hor:.1f}-{qtd:.2f}"

                ok = db_engine.inserir_registro(
                    dv.strftime("%Y-%m-%d"), produto, resp, placa, frota,
                    vl, qtd, hor, identify_category(produto), filename, hv)

                if ok:   stats["inseridos"]  += 1
                else:    stats["duplicados"] += 1

        return stats
