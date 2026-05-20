# =================================================================
# EXPORT_UTILS.PY — Exportação PDF e Excel compartilhada
# =================================================================
import io
import pandas as pd
from datetime import datetime


# ── Excel genérico ────────────────────────────────────────────────
def df_to_excel(df: pd.DataFrame, sheet_name: str = "Dados") -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

        df.to_excel(writer, index=False, sheet_name=sheet_name)
        ws = writer.sheets[sheet_name]

        # Estilo cabeçalho
        header_fill = PatternFill("solid", fgColor="10B981")
        header_font = Font(color="FFFFFF", bold=True, size=11)
        alt_fill    = PatternFill("solid", fgColor="1A1D23")
        dark_fill   = PatternFill("solid", fgColor="111318")
        data_font   = Font(color="E2E8F0", size=10)
        thin = Border(
            left=Side(style="thin", color="2A2D35"),
            right=Side(style="thin", color="2A2D35"),
            top=Side(style="thin", color="2A2D35"),
            bottom=Side(style="thin", color="2A2D35"))

        for ci, cell in enumerate(ws[1], 1):
            cell.fill      = header_fill
            cell.font      = header_font
            cell.border    = thin
            cell.alignment = Alignment(horizontal="center")
            ws.column_dimensions[
                cell.column_letter].width = 18

        for ri, row in enumerate(ws.iter_rows(min_row=2), 2):
            fill = dark_fill if ri % 2 == 0 else alt_fill
            for cell in row:
                cell.fill      = fill
                cell.font      = data_font
                cell.border    = thin
                cell.alignment = Alignment(horizontal="center")

        ws.sheet_view.showGridLines = False

    return buf.getvalue()


def df_to_excel_multi(sheets: dict) -> bytes:
    """Gera Excel com múltiplas abas. sheets = {'Nome Aba': df, ...}"""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

        header_fill = PatternFill("solid", fgColor="10B981")
        header_font = Font(color="FFFFFF", bold=True, size=11)
        alt_fill    = PatternFill("solid", fgColor="1A1D23")
        dark_fill   = PatternFill("solid", fgColor="111318")
        data_font   = Font(color="E2E8F0", size=10)
        thin = Border(
            left=Side(style="thin", color="2A2D35"),
            right=Side(style="thin", color="2A2D35"),
            top=Side(style="thin", color="2A2D35"),
            bottom=Side(style="thin", color="2A2D35"))

        for sheet_name, df in sheets.items():
            nome = str(sheet_name)[:31]
            df.to_excel(writer, index=False, sheet_name=nome)
            ws = writer.sheets[nome]
            for cell in ws[1]:
                cell.fill      = header_fill
                cell.font      = header_font
                cell.border    = thin
                cell.alignment = Alignment(horizontal="center")
                ws.column_dimensions[cell.column_letter].width = 18
            for ri, row in enumerate(ws.iter_rows(min_row=2), 2):
                fill = dark_fill if ri % 2 == 0 else alt_fill
                for cell in row:
                    cell.fill      = fill
                    cell.font      = data_font
                    cell.border    = thin
                    cell.alignment = Alignment(horizontal="center")
            ws.sheet_view.showGridLines = False

    return buf.getvalue()


# ── PDF genérico ──────────────────────────────────────────────────
def df_to_pdf(df: pd.DataFrame, titulo: str,
              subtitulo: str = "", landscape: bool = True) -> bytes:
    from reportlab.lib.pagesizes import A4, landscape as rl_landscape
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import (SimpleDocTemplate, Table,
                                    TableStyle, Paragraph, Spacer)
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    buf = io.BytesIO()
    pagesize = rl_landscape(A4) if landscape else A4
    doc = SimpleDocTemplate(buf, pagesize=pagesize,
                            leftMargin=1.5*cm, rightMargin=1.5*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)
    stls = getSampleStyleSheet()

    title_style = ParagraphStyle("T", parent=stls["Title"],
                                  fontSize=16,
                                  textColor=colors.HexColor("#10B981"),
                                  spaceAfter=4)
    sub_style   = ParagraphStyle("S", parent=stls["Normal"],
                                  fontSize=9,
                                  textColor=colors.HexColor("#64748B"),
                                  spaceAfter=14)

    elems = [
        Paragraph(titulo, title_style),
        Paragraph(
            subtitulo or
            f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')} "
            f"· {len(df)} registros",
            sub_style),
    ]

    # Monta dados da tabela
    cols = df.columns.tolist()
    col_w = [(pagesize[0] - 3*cm) / len(cols)] * len(cols)
    data  = [cols] + df.astype(str).values.tolist()

    tbl = Table(data, colWidths=col_w, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0), colors.HexColor("#10B981")),
        ("TEXTCOLOR",     (0,0),(-1,0), colors.white),
        ("FONTNAME",      (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,0), 8),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),
            [colors.HexColor("#1A1D23"), colors.HexColor("#111318")]),
        ("TEXTCOLOR",     (0,1),(-1,-1), colors.HexColor("#E2E8F0")),
        ("FONTSIZE",      (0,1),(-1,-1), 7),
        ("ALIGN",         (0,0),(-1,-1), "CENTER"),
        ("BOX",           (0,0),(-1,-1), 0.5, colors.HexColor("#2A2D35")),
        ("INNERGRID",     (0,0),(-1,-1), 0.2,  colors.HexColor("#2A2D35")),
        ("TOPPADDING",    (0,0),(-1,-1), 4),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
    ]))
    elems.append(tbl)
    doc.build(elems)
    return buf.getvalue()


# ── Botões de download prontos para usar no Streamlit ─────────────
def botoes_download(st, df: pd.DataFrame, nome_base: str,
                    titulo_pdf: str, colunas_pdf: list = None,
                    sheets_excel: dict = None):
    """
    Renderiza os botões de download PDF e Excel lado a lado.
    
    Parâmetros:
        st          — instância do streamlit
        df          — DataFrame principal
        nome_base   — nome base do arquivo (ex: 'registros')
        titulo_pdf  — título que aparece no PDF
        colunas_pdf — lista de colunas a incluir no PDF (None = todas)
        sheets_excel— dict de {nome_aba: df} para Excel multi-aba
    """
    data_str = datetime.now().strftime("%Y%m%d")
    c1, c2, _ = st.columns([1, 1, 6])

    # PDF
    with c1:
        try:
            df_pdf = df[colunas_pdf].copy() if colunas_pdf else df.copy()
            # Limita a 500 linhas no PDF para não estourar memória
            if len(df_pdf) > 500:
                df_pdf = df_pdf.tail(500)
                titulo_final = titulo_pdf + " (últimas 500 linhas)"
            else:
                titulo_final = titulo_pdf
            pdf_bytes = df_to_pdf(df_pdf, titulo_final)
            st.download_button(
                "📄  PDF",
                pdf_bytes,
                f"{nome_base}_{data_str}.pdf",
                "application/pdf",
                use_container_width=True)
        except Exception as e:
            st.error(f"Erro PDF: {e}")

    # Excel
    with c2:
        try:
            if sheets_excel:
                xls_bytes = df_to_excel_multi(sheets_excel)
            else:
                xls_bytes = df_to_excel(df)
            st.download_button(
                "📗  Excel",
                xls_bytes,
                f"{nome_base}_{data_str}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)
        except Exception as e:
            st.error(f"Erro Excel: {e}")
