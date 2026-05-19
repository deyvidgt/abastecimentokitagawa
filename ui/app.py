# =================================================================
# UI/APP.PY — Janela principal e sidebar (mixin-based)
# =================================================================
import os
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import filedialog
from tkinter import messagebox

import customtkinter as ctk
from PIL import Image

from config import (C_BG, C_SURFACE, C_BORDER, C_ACCENT,
                    C_TEXT, C_MUTED, C_SUCCESS, C_WARNING, C_DANGER,
                    CAMINHO_LOGO)
from database import DataEngine
from etl import ProcessorETL
from export import ExportManager
from ui.widgets import make_separator, embed_chart, card
import pandas as pd

# ── Importar todas as views (mixin pattern) ───────────────────────
from ui.views.dashboard      import DashboardView
from ui.views.frota          import FrotaView
from ui.views.custos         import CustosView
from ui.views.registros      import RegistrosView
from ui.views.cadastros      import CadastrosView
from ui.views.importacao     import ImportacaoView
from ui.views.configuracoes  import ConfiguracoesView


class ERP_Mutima(
    ctk.CTk,
    DashboardView,
    FrotaView,
    CustosView,
    RegistrosView,
    CadastrosView,
    ImportacaoView,
    ConfiguracoesView,
):
    def __init__(self):
        super().__init__()
        self.db        = DataEngine()
        self.processor = ProcessorETL()
        self.exporter  = ExportManager()
        self._active_btn = None

        # Filtros de período globais
        self._filter_start = tk.StringVar()
        self._filter_end   = tk.StringVar()
        self._reset_filters()

        self.title("KITAGAWA — Sistema de Gestão de Ativos v11")
        self.geometry("1680x980")
        self.configure(fg_color=C_BG)

        if os.path.exists("logo.ico"):
            self.iconbitmap("logo.ico")

        self.load_assets()
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=1, sticky="nsew", padx=24, pady=24)
        self.show_dashboard()

    # ── Troca de tema sem reiniciar ───────────────────────────────
    def _rebuild_ui(self):
        """
        Reconstrói sidebar + view atual após troca de tema.
        Chamado via after() para garantir que estamos fora de
        qualquer callback de widget que será destruído.
        """
        import config  # lê as cores já atualizadas pelo apply_theme_live

        # Atualiza cor de fundo da janela raiz
        self.configure(fg_color=config.C_BG)

        # Destrói sidebar e container atuais
        self.sidebar.destroy()
        self.container.destroy()

        # Recria container
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=1, sticky="nsew", padx=24, pady=24)

        # Recria sidebar (usará as variáveis de módulo já atualizadas)
        self.setup_sidebar()

        # Volta para o dashboard com as novas cores
        self.show_dashboard()

    # ── Filtros ───────────────────────────────────────────────────
    def _reset_filters(self):
        self._filter_start.set("01-01-2000")
        self._filter_end.set(datetime.now().strftime("%d-%m-%Y"))

    def _get_filtered_df(self):
        try:
            s = datetime.strptime(
                self._filter_start.get(), "%d-%m-%Y").strftime("%Y-%m-%d")
            e = datetime.strptime(
                self._filter_end.get(), "%d-%m-%Y").strftime("%Y-%m-%d")
            df = self.db.get_dataframe(
                "SELECT * FROM registros WHERE data >= ? AND data <= ? ORDER BY data",
                (s, e))
        except Exception:
            df = self.db.get_dataframe("SELECT * FROM registros")
        for col in ["valor","quantidade","horimetro"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        df["data"] = pd.to_datetime(df["data"], errors="coerce")
        return df

    # ── Exportação ────────────────────────────────────────────────
    def _export_pdf(self):
        df = self._get_filtered_df()
        if df.empty:
            messagebox.showwarning("Atenção","Sem dados no período."); return
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF","*.pdf")],
            initialfile=f"relatorio_frota_{datetime.now().strftime('%Y%m%d')}.pdf")
        if not path: return
        ok = self.exporter.export_pdf(
            df, path,
            f"Relatório de Frota · "
            f"{self._filter_start.get()} a {self._filter_end.get()}")
        if ok:
            messagebox.showinfo("Sucesso", f"PDF exportado:\n{path}")

    def _export_excel(self):
        df = self._get_filtered_df()
        if df.empty:
            messagebox.showwarning("Atenção","Sem dados no período."); return
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel","*.xlsx")],
            initialfile=f"relatorio_frota_{datetime.now().strftime('%Y%m%d')}.xlsx")
        if not path: return
        ok = self.exporter.export_excel(df, path)
        if ok:
            messagebox.showinfo("Sucesso", f"Excel exportado:\n{path}")

    # ── Assets ────────────────────────────────────────────────────
    def load_assets(self):
        try:
            if os.path.exists(CAMINHO_LOGO):
                img = Image.open(CAMINHO_LOGO)
                self.img_sidebar = ctk.CTkImage(img, size=(130,130))
                self.img_header  = ctk.CTkImage(img, size=(36,36))
            else:
                self.img_sidebar = self.img_header = None
        except Exception:
            self.img_sidebar = self.img_header = None

    # ── Sidebar ───────────────────────────────────────────────────
    def setup_sidebar(self):
        import config  # garante cores atualizadas mesmo após troca de tema
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0,
                                     fg_color=config.C_SURFACE,
                                     border_width=1, border_color=config.C_BORDER)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.pack_propagate(False)
        self._active_btn = None  # reseta botão ativo ao reconstruir

        if self.img_sidebar:
            ctk.CTkLabel(self.sidebar,
                         image=self.img_sidebar, text="").pack(pady=(32,8))
        ctk.CTkLabel(self.sidebar, text="ABASTECIMENTOS",
                     font=ctk.CTkFont("Arial",15,"bold"),
                     text_color=config.C_TEXT).pack()
        ctk.CTkLabel(self.sidebar, text="Enterprise v11.0",
                     font=ctk.CTkFont("Arial",10),
                     text_color=config.C_MUTED).pack(pady=(2,18))
        make_separator(self.sidebar)

        self._nav_group("ANALÍTICOS")
        self._nav_btn("📊  Dashboard",          self.show_dashboard)
        self._nav_btn("🚛  Gestão de Frota",    self.show_frota)
        self._nav_btn("💸  Centro de Custos",   self.show_custos)
        self._nav_btn("➕  Novo Registro",      self.show_novo_registro)
        self._nav_btn("📋  Registros",          self.show_registros)
        self._nav_group("CADASTROS")
        self._nav_btn("🚗  Veículos",           self.show_veiculos)
        self._nav_btn("👤  Condutores",          self.show_condutores)
        self._nav_group("SISTEMA")
        self._nav_btn("🗂️  Log de Importações", self.show_import_log)
        self._nav_btn("⚙️  Configurações",      self.show_configuracoes)

        ctk.CTkButton(
            self.sidebar, text="📥  IMPORTAR LOTE",
            fg_color=config.C_ACCENT, hover_color="#2563EB", height=44,
            font=ctk.CTkFont("Arial",13,"bold"), corner_radius=10,
            command=self.start_import_thread,
        ).pack(pady=20, padx=20, fill="x", side="bottom")

        st = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        st.pack(side="bottom", fill="x", padx=20, pady=(0,8))
        ctk.CTkLabel(st, text="● DB Conectado",
                     text_color=config.C_SUCCESS,
                     font=ctk.CTkFont("Arial",11)).pack(side="left")

    def _nav_group(self, t):
        import config
        ctk.CTkLabel(self.sidebar, text=t,
                     font=ctk.CTkFont("Arial",10,"bold"),
                     text_color=config.C_MUTED).pack(pady=(18,4), padx=20, anchor="w")

    def _nav_btn(self, text, cmd):
        import config
        btn = ctk.CTkButton(
            self.sidebar, text=text, anchor="w", height=40,
            fg_color="transparent", text_color=config.C_TEXT,
            hover_color=config.C_BORDER, font=ctk.CTkFont("Arial",13),
            corner_radius=8)
        btn.configure(command=lambda b=btn, c=cmd: self._nav_click(c, b))
        btn.pack(fill="x", padx=12, pady=2)
        return btn

    def _nav_click(self, cmd, btn):
        import config
        if self._active_btn:
            self._active_btn.configure(
                fg_color="transparent", text_color=config.C_TEXT)
        if btn:
            btn.configure(fg_color=config.C_ACCENT, text_color="white")
            self._active_btn = btn
        cmd()

    # ── Helpers de layout ─────────────────────────────────────────
    def clear_container(self):
        for w in self.container.winfo_children():
            w.destroy()

    def render_header(self, title, subtitle=""):
        import config
        f = ctk.CTkFrame(self.container, fg_color="transparent")
        f.pack(fill="x", pady=(0,14))
        r = ctk.CTkFrame(f, fg_color="transparent")
        r.pack(fill="x")
        if self.img_header:
            ctk.CTkLabel(r, image=self.img_header,
                         text="").pack(side="left", padx=(0,10))
        ctk.CTkLabel(r, text=title,
                     font=ctk.CTkFont("Arial",26,"bold"),
                     text_color=config.C_TEXT).pack(side="left")
        if subtitle:
            ctk.CTkLabel(f, text=subtitle,
                         font=ctk.CTkFont("Arial",11),
                         text_color=config.C_MUTED).pack(anchor="w", padx=2)
        make_separator(f, pady=(10,0))

    def render_filter_bar(self, on_apply):
        import config
        bar = card(self.container)
        bar.pack(fill="x", pady=(0,12))
        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=10)

        ctk.CTkLabel(inner, text="PERÍODO:",
                     font=ctk.CTkFont("Arial",10,"bold"),
                     text_color=config.C_MUTED).pack(side="left", padx=(0,8))
        ctk.CTkEntry(inner, textvariable=self._filter_start,
                     width=110, height=32).pack(side="left", padx=(0,4))
        ctk.CTkLabel(inner, text="→",
                     text_color=config.C_MUTED).pack(side="left", padx=4)
        ctk.CTkEntry(inner, textvariable=self._filter_end,
                     width=110, height=32).pack(side="left", padx=(0,12))

        def quick(days):
            self._filter_end.set(datetime.now().strftime("%d-%m-%Y"))
            self._filter_start.set(
                (datetime.now()-timedelta(days=days)).strftime("%d-%m-%Y"))
            on_apply()

        for label, days in [("7d",7),("30d",30),("90d",90),("1 ano",365),("Tudo",9999)]:
            ctk.CTkButton(
                inner, text=label, width=52, height=30,
                fg_color=config.C_BORDER, hover_color=config.C_ACCENT,
                font=ctk.CTkFont("Arial",10),
                command=lambda d=days: quick(d),
            ).pack(side="left", padx=3)

        ctk.CTkButton(inner, text="🔍 Aplicar", width=80, height=30,
                      fg_color=config.C_ACCENT,
                      font=ctk.CTkFont("Arial",10,"bold"),
                      command=on_apply).pack(side="left", padx=(10,0))

        ctk.CTkFrame(inner, width=1,
                     fg_color=config.C_BORDER).pack(side="left", fill="y", padx=12)
        ctk.CTkButton(inner, text="📄 PDF", width=72, height=30,
                      fg_color="#DC2626", hover_color="#B91C1C",
                      font=ctk.CTkFont("Arial",10,"bold"),
                      command=self._export_pdf).pack(side="left", padx=3)
        ctk.CTkButton(inner, text="📊 Excel", width=80, height=30,
                      fg_color="#16A34A", hover_color="#15803D",
                      font=ctk.CTkFont("Arial",10,"bold"),
                      command=self._export_excel).pack(side="left", padx=3)

    # ── Estado vazio ──────────────────────────────────────────────
    def show_empty_state(self):
        import config
        f = ctk.CTkFrame(self.container, fg_color="transparent")
        f.pack(expand=True)
        if self.img_sidebar:
            ctk.CTkLabel(f, image=self.img_sidebar,
                         text="").pack(pady=(60,20))
        ctk.CTkLabel(f, text="SEM DADOS",
                     font=ctk.CTkFont("Arial",32,"bold"),
                     text_color=config.C_MUTED).pack()
        ctk.CTkLabel(f, text="Use  📥 IMPORTAR LOTE  para carregar planilhas.",
                     font=ctk.CTkFont("Arial",14),
                     text_color=config.C_MUTED).pack(pady=8)
        ctk.CTkButton(f, text="📥  Importar agora",
                      fg_color=config.C_ACCENT, height=44,
                      font=ctk.CTkFont("Arial",13,"bold"),
                      command=self.start_import_thread).pack(pady=16)
