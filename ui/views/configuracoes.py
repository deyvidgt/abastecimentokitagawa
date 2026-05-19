# UI/VIEWS/CONFIGURACOES.PY
import shutil
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime

from config import C_ACCENT, C_SUCCESS, C_BORDER, C_MUTED, C_TEXT, C_BG, C_SURFACE, DB_NAME
from ui.widgets import card
from theme import THEMES, save_theme, get_saved_theme_name, apply_theme_live


class ConfiguracoesView:

    def show_configuracoes(self):
        self.clear_container()
        self.render_header("CONFIGURAÇÕES", "Personalize o sistema")

        scroll = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        # ── Identidade ────────────────────────────────────────────
        sec1 = card(scroll); sec1.pack(fill="x", pady=(0,12), padx=2)
        ctk.CTkLabel(sec1, text="🏢  IDENTIDADE DA EMPRESA",
                     font=ctk.CTkFont("Arial",12,"bold"),
                     text_color=C_MUTED).pack(anchor="w", padx=20, pady=(16,8))
        f1 = ctk.CTkFrame(sec1, fg_color="transparent")
        f1.pack(fill="x", padx=20, pady=(0,16))

        ctk.CTkLabel(f1, text="Nome da empresa:",
                     font=ctk.CTkFont("Arial",11),
                     text_color=C_TEXT).grid(row=0, column=0, sticky="w", pady=6)
        ent_empresa = ctk.CTkEntry(f1, width=340, height=36)
        ent_empresa.insert(0, self.db.get_config("empresa","KITAGAWA"))
        ent_empresa.grid(row=0, column=1, padx=16)

        ctk.CTkLabel(f1, text="Caminho do logo (.png):",
                     font=ctk.CTkFont("Arial",11),
                     text_color=C_TEXT).grid(row=1, column=0, sticky="w", pady=6)
        ent_logo = ctk.CTkEntry(f1, width=280, height=36)
        ent_logo.insert(0, self.db.get_config("logo_path","logo.png"))
        ent_logo.grid(row=1, column=1, padx=16, sticky="w")

        def browse_logo():
            p = filedialog.askopenfilename(
                filetypes=[("Imagens","*.png *.jpg *.ico")])
            if p:
                ent_logo.delete(0, "end")
                ent_logo.insert(0, p)

        ctk.CTkButton(f1, text="📂", width=40, height=36, fg_color=C_BORDER,
                      command=browse_logo).grid(row=1, column=2, padx=4)

        # ── Banco de dados ────────────────────────────────────────
        sec2 = card(scroll); sec2.pack(fill="x", pady=(0,12), padx=2)
        ctk.CTkLabel(sec2, text="🗄️  BANCO DE DADOS",
                     font=ctk.CTkFont("Arial",12,"bold"),
                     text_color=C_MUTED).pack(anchor="w", padx=20, pady=(16,8))
        f2 = ctk.CTkFrame(sec2, fg_color="transparent")
        f2.pack(fill="x", padx=20, pady=(0,16))

        ctk.CTkLabel(f2, text="Arquivo do banco (.db):",
                     font=ctk.CTkFont("Arial",11),
                     text_color=C_TEXT).grid(row=0, column=0, sticky="w", pady=6)
        ent_db = ctk.CTkEntry(f2, width=280, height=36)
        ent_db.insert(0, self.db.get_config("db_path", DB_NAME))
        ent_db.grid(row=0, column=1, padx=16, sticky="w")
        ctk.CTkLabel(f2, text="(aplicado no próximo início)",
                     font=ctk.CTkFont("Arial",9),
                     text_color=C_MUTED).grid(row=0, column=2, padx=4)

        def backup_agora():
            dst = filedialog.asksaveasfilename(
                defaultextension=".db",
                filetypes=[("SQLite","*.db")],
                initialfile=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
            if dst:
                shutil.copy2(DB_NAME, dst)
                messagebox.showinfo("Backup", f"Salvo em:\n{dst}")

        ctk.CTkButton(f2, text="💾  Fazer backup agora",
                      fg_color=C_SUCCESS, height=36,
                      command=backup_agora).grid(
                          row=1, column=0, columnspan=2, sticky="w", pady=(8,0))

        # ── Tema visual ───────────────────────────────────────────
        sec3 = card(scroll); sec3.pack(fill="x", pady=(0,12), padx=2)
        ctk.CTkLabel(sec3, text="🎨  TEMA VISUAL",
                     font=ctk.CTkFont("Arial",12,"bold"),
                     text_color=C_MUTED).pack(anchor="w", padx=20, pady=(16,8))
        ctk.CTkLabel(sec3, text="Clique num tema e depois em Aplicar — sem reiniciar.",
                     font=ctk.CTkFont("Arial",10),
                     text_color=C_MUTED).pack(anchor="w", padx=20, pady=(0,10))

        current_name   = get_saved_theme_name()
        selected_theme = tk.StringVar(value=current_name)
        theme_cards    = {}

        grid_outer = ctk.CTkFrame(sec3, fg_color="transparent")
        grid_outer.pack(fill="x", padx=16, pady=(0, 6))

        def _select(name, card_frame, check_label):
            for nm, (cf, cl) in theme_cards.items():
                t = THEMES[nm]
                cf.configure(border_color=t["C_BORDER"], border_width=1)
                cl.configure(text="")
            t = THEMES[name]
            card_frame.configure(border_color=t["C_ACCENT"], border_width=2)
            check_label.configure(text="✔  Selecionado")
            selected_theme.set(name)

        def _bind_all(widget, callback):
            widget.bind("<Button-1>", lambda e: callback())
            for child in widget.winfo_children():
                _bind_all(child, callback)

        for col, (name, td) in enumerate(THEMES.items()):
            is_active = (name == current_name)
            b_clr = td["C_ACCENT"] if is_active else td["C_BORDER"]
            bw    = 2              if is_active else 1

            outer = ctk.CTkFrame(
                grid_outer,
                fg_color=td["C_SURFACE"],
                corner_radius=12,
                border_width=bw,
                border_color=b_clr,
                width=185, height=168,
            )
            outer.grid(row=0, column=col, padx=6, pady=4, sticky="nsew")
            outer.grid_propagate(False)
            grid_outer.grid_columnconfigure(col, weight=1)

            dots = ctk.CTkFrame(outer, fg_color="transparent")
            dots.pack(pady=(14,6))
            for clr in [td["C_ACCENT"], td["C_SUCCESS"], td["C_WARNING"], td["C_DANGER"]]:
                ctk.CTkFrame(dots, width=20, height=20, corner_radius=10,
                             fg_color=clr).pack(side="left", padx=3)

            pf = ctk.CTkFrame(outer, fg_color=td["C_BG"], corner_radius=8, height=48)
            pf.pack(fill="x", padx=10, pady=4)
            pf.pack_propagate(False)
            ctk.CTkFrame(pf, height=12, corner_radius=3,
                         fg_color=td["C_ACCENT"]).pack(fill="x", padx=8, pady=(7,3))
            rf = ctk.CTkFrame(pf, fg_color="transparent")
            rf.pack(fill="x", padx=8)
            ctk.CTkFrame(rf, height=7, corner_radius=2,
                         fg_color=td["C_SURFACE"]).pack(side="left", fill="x", expand=True, padx=(0,3))
            ctk.CTkFrame(rf, height=7, corner_radius=2,
                         fg_color=td["C_BORDER"]).pack(side="left", fill="x", expand=True)

            ctk.CTkLabel(outer, text=td["label"],
                         font=ctk.CTkFont("Arial", 11, "bold"),
                         text_color=td["C_TEXT"]).pack(pady=(6,2))

            check_lbl = ctk.CTkLabel(
                outer,
                text="✔  Ativo" if is_active else "",
                font=ctk.CTkFont("Arial", 9),
                text_color=td["C_ACCENT"])
            check_lbl.pack()

            theme_cards[name] = (outer, check_lbl)
            _bind_all(outer, lambda n=name, cf=outer, cl=check_lbl: _select(n, cf, cl))

        # ── Botão aplicar (sem reiniciar) ─────────────────────────
        def aplicar_tema():
            name = selected_theme.get()
            if name == current_name:
                messagebox.showinfo("Tema", "Este tema já está ativo.")
                return
            # apply_theme_live salva, propaga as cores e agenda _rebuild_ui
            # via after(50) — a UI troca instantaneamente sem reiniciar.
            if not apply_theme_live(self, name):
                messagebox.showerror("Erro", "Não foi possível aplicar o tema.")

        ctk.CTkButton(
            sec3,
            text="🎨  APLICAR TEMA  (instantâneo, sem reiniciar)",
            fg_color=C_ACCENT, hover_color="#1D4ED8",
            height=44, corner_radius=10,
            font=ctk.CTkFont("Arial",13,"bold"),
            command=aplicar_tema,
        ).pack(fill="x", padx=20, pady=(6,20))

        # ── Salvar identidade / DB ────────────────────────────────
        def salvar_configs():
            self.db.set_config("empresa",   ent_empresa.get().strip())
            self.db.set_config("logo_path", ent_logo.get().strip())
            self.db.set_config("db_path",   ent_db.get().strip())
            messagebox.showinfo("Salvo",
                "Configurações salvas.\n"
                "Reinicie para aplicar mudanças de banco.")

        ctk.CTkButton(
            scroll,
            text="💾  SALVAR CONFIGURAÇÕES",
            fg_color=C_SUCCESS, hover_color="#15803D",
            height=48, font=ctk.CTkFont("Arial",14,"bold"),
            corner_radius=10,
            command=salvar_configs,
        ).pack(fill="x", padx=2, pady=(4,16))
