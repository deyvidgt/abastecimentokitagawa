# UI/VIEWS/IMPORTACAO.PY — Importação em lote + log
import os
import threading
import customtkinter as ctk
from tkinter import messagebox, filedialog

from config import C_SURFACE, C_BORDER, C_ACCENT, C_TEXT, C_MUTED, C_SUCCESS, C_WARNING, C_DANGER
from ui.widgets import card, style_tree
from ui.dialogs import NovasPlacasDialog


class ImportacaoView:

    # =============================================================
    # IMPORTAÇÃO
    # =============================================================
    def start_import_thread(self):
        pasta = filedialog.askdirectory(
            title="Selecione a pasta com os arquivos Excel")
        if not pasta: return

        arquivos = [f for f in os.listdir(pasta)
                    if f.lower().endswith((".xlsx",".xls"))]
        if not arquivos:
            messagebox.showwarning("Atenção","Nenhum .xlsx/.xls encontrado.")
            return

        self._scan_and_import(pasta, arquivos)

    def _scan_and_import(self, pasta, arquivos):
        known = self.db.placas_cadastradas()
        novas = set()
        for arq in arquivos:
            novas |= self.processor.scan_new_plates(
                os.path.join(pasta, arq), known)

        if novas:
            dlg = NovasPlacasDialog(self, novas)
            for placa, info in dlg.result.items():
                self.db.execute_query(
                    "INSERT OR IGNORE INTO veiculos (placa,modelo,tipo,status) VALUES (?,?,?,?)",
                    (placa, info["modelo"] or placa, info["tipo"], "Ativo"))
            n = len(dlg.result)
            if n:
                messagebox.showinfo("Cadastro",
                    f"{n} veículo(s) cadastrado(s) com sucesso!")

        # Janela de progresso
        self.overlay = ctk.CTkToplevel(self)
        self.overlay.geometry("500x340")
        self.overlay.title("Importando…")
        self.overlay.attributes("-topmost", True)
        self.overlay.configure(fg_color=C_SURFACE)
        self.overlay.resizable(False, False)

        ctk.CTkLabel(self.overlay, text="PROCESSANDO ARQUIVOS",
                     font=ctk.CTkFont("Arial",16,"bold"),
                     text_color=C_TEXT).pack(pady=(28,6))
        self.pbar = ctk.CTkProgressBar(self.overlay, width=420, height=12,
                                        progress_color=C_ACCENT)
        self.pbar.pack(pady=8); self.pbar.set(0)
        self.lbl_prog = ctk.CTkLabel(self.overlay, text="Iniciando…",
                                      font=ctk.CTkFont("Arial",11),
                                      text_color=C_MUTED)
        self.lbl_prog.pack(pady=4)
        self.log_box = ctk.CTkTextbox(self.overlay, height=160,
                                       font=ctk.CTkFont("Courier",9),
                                       fg_color="#111318",
                                       text_color=C_MUTED, border_width=0)
        self.log_box.pack(fill="x", padx=20, pady=10)

        threading.Thread(target=self._run_import,
                         args=(pasta, arquivos), daemon=True).start()

    def _run_import(self, pasta, arquivos):
        totals = {"inseridos": 0, "duplicados": 0, "erros": 0}
        n = len(arquivos)

        for i, arq in enumerate(arquivos):
            texto = f"[{i+1}/{n}] {arq}"
            self.after(0, lambda t=texto: self.lbl_prog.configure(text=t))
            self.after(0, lambda a=arq: (
                self.log_box.insert("end", f"\n▶ {a}\n"),
                self.log_box.see("end")
            ))

            res = self.processor.process_excel(os.path.join(pasta, arq), self.db)
            totals["inseridos"]  += res["inseridos"]
            totals["duplicados"] += res["duplicados"]
            totals["erros"]      += res["erros"]

            detalhes = res["detalhes"][:]

            # BUG FIX: era uma generator expression dentro de lista:
            #   [(gen_expr), log_box.see()]
            # Generator expressions nunca são iteradas automaticamente —
            # os inserts jamais eram executados e o log ficava em branco.
            # Corrigido para list comprehension [list_comp, see()], que
            # força a avaliação de todos os elementos.
            self.after(0, lambda lns=detalhes: [
                [self.log_box.insert("end", f"  {ln}\n") for ln in lns],
                self.log_box.see("end")
            ])

            prog = (i + 1) / n
            self.after(0, lambda p=prog: self.pbar.set(p))

        self.after(0, lambda: self._finish_import(totals, n))

    def _finish_import(self, totals, n_arquivos):
        """Chamado na thread principal após o processamento."""
        self.overlay.destroy()
        messagebox.showinfo("Importação Concluída",
            f"✅ Inseridos:   {totals['inseridos']}\n"
            f"🔁 Duplicados: {totals['duplicados']}\n"
            f"❌ Erros:       {totals['erros']}\n\n"
            f"Arquivos: {n_arquivos}")
        self.show_dashboard()

    # =============================================================
    # LOG DE IMPORTAÇÕES
    # =============================================================
    def show_import_log(self):
        self.clear_container()
        self.render_header("LOG DE IMPORTAÇÕES",
                           "Histórico detalhado de arquivos processados")

        df = self.db.get_dataframe(
            "SELECT arquivo,data_import,inseridos,duplicados,erros,detalhes "
            "FROM import_log ORDER BY id DESC LIMIT 60")

        scroll = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        if df.empty:
            ctk.CTkLabel(scroll, text="Nenhuma importação registrada.",
                         font=ctk.CTkFont("Arial",14),
                         text_color=C_MUTED).pack(pady=40)
            return

        for _, row in df.iterrows():
            c = card(scroll); c.pack(fill="x", pady=6, padx=2)
            top = ctk.CTkFrame(c, fg_color="transparent")
            top.pack(fill="x", padx=16, pady=(10,4))
            ctk.CTkLabel(top, text=f"📂 {row['arquivo']}",
                         font=ctk.CTkFont("Arial",13,"bold"),
                         text_color=C_TEXT).pack(side="left")
            ctk.CTkLabel(top, text=str(row["data_import"])[:16],
                         font=ctk.CTkFont("Arial",10),
                         text_color=C_MUTED).pack(side="right")

            pills = ctk.CTkFrame(c, fg_color="transparent")
            pills.pack(fill="x", padx=16, pady=(0,4))
            for lbl, clr in [(f"✅ {row['inseridos']} inseridos",  C_SUCCESS),
                              (f"🔁 {row['duplicados']} duplicados",C_WARNING),
                              (f"❌ {row['erros']} erros",          C_DANGER)]:
                ctk.CTkLabel(pills, text=lbl,
                             font=ctk.CTkFont("Arial",10),
                             text_color=clr).pack(side="left", padx=(0,16))

            if row["detalhes"]:
                det = ctk.CTkTextbox(c, height=72,
                                      font=ctk.CTkFont("Courier",9),
                                      fg_color="#111318",
                                      text_color=C_MUTED, border_width=0)
                det.insert("end", row["detalhes"])
                det.configure(state="disabled")
                det.pack(fill="x", padx=16, pady=(0,10))
