# UI/VIEWS/CADASTROS.PY — Veículos e Condutores
import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime

from config import (C_SURFACE, C_BORDER, C_ACCENT, C_SUCCESS,
                    C_DANGER, C_TEXT, C_MUTED, C_WARNING)
from ui.widgets import card, style_tree
from ui.dialogs import (TIPOS_VEICULO, TIPOS_SEM_PLACA,
                        label_identificador, gerar_id,
                        open_edit_veiculo)


class CadastrosView:

    # =============================================================
    # VEÍCULOS
    # =============================================================
    def show_veiculos(self):
        self.clear_container()
        self.render_header("CADASTRO DE VEÍCULOS")

        form = card(self.container)
        form.pack(pady=8, padx=4, fill="x")

        lbl_id = ctk.CTkLabel(form, text="Placa",
                               font=ctk.CTkFont("Arial",11), text_color=C_MUTED)
        lbl_id.grid(row=0,column=0,padx=16,pady=(16,2),sticky="w")
        ent_placa = ctk.CTkEntry(form, width=200, height=38,
                                  placeholder_text="ex: ABC1234")
        ent_placa.grid(row=1,column=0,padx=16,pady=(0,16))

        ctk.CTkLabel(form,text="Modelo",font=ctk.CTkFont("Arial",11),
                     text_color=C_MUTED).grid(row=0,column=1,padx=16,pady=(16,2),sticky="w")
        ent_modelo = ctk.CTkEntry(form, width=200, height=38)
        ent_modelo.grid(row=1,column=1,padx=16,pady=(0,16))

        ctk.CTkLabel(form,text="Nº Frota (opcional)",font=ctk.CTkFont("Arial",11),
                     text_color=C_MUTED).grid(row=0,column=2,padx=16,pady=(16,2),sticky="w")
        ent_frota = ctk.CTkEntry(form, width=140, height=38,
                                  placeholder_text="ex: 42")
        ent_frota.grid(row=1,column=2,padx=16,pady=(0,16))

        ctk.CTkLabel(form,text="Tipo",font=ctk.CTkFont("Arial",11),
                     text_color=C_MUTED).grid(row=0,column=3,padx=16,pady=(16,2),sticky="w")
        tipo_cb = ctk.CTkComboBox(form, values=TIPOS_VEICULO, width=200, height=38)
        tipo_cb.grid(row=1,column=3,padx=16,pady=(0,16))

        btn_gerar = ctk.CTkButton(form, text="🔢 Gerar ID", width=100, height=38,
                                   fg_color=C_WARNING, hover_color="#D97706",
                                   font=ctk.CTkFont("Arial",11,"bold"))
        btn_gerar.grid(row=1,column=4,padx=(0,8),pady=(0,16))
        btn_gerar.grid_remove()

        def on_tipo_change(t):
            sem = t in TIPOS_SEM_PLACA
            lbl_id.configure(text="Identificador" if sem else "Placa")
            ent_placa.configure(
                placeholder_text="ex: DRONE-001" if sem else "ex: ABC1234")
            if sem: btn_gerar.grid()
            else:   btn_gerar.grid_remove()

        tipo_cb.configure(command=on_tipo_change)
        btn_gerar.configure(command=lambda: (
            ent_placa.delete(0,"end"),
            ent_placa.insert(0, gerar_id(tipo_cb.get(), self.db))))

        def salvar():
            p = ent_placa.get().upper().strip()
            m = ent_modelo.get().upper().strip()
            campo = label_identificador(tipo_cb.get())
            if not p or not m:
                messagebox.showwarning("Atenção",
                    f"{campo} e Modelo são obrigatórios."); return

            # BUG FIX: antes o número de frota era salvo na coluna `status`
            # como "Frota:123", corrompendo o campo (deveria ser Ativo/Inativo/
            # Manutenção). O número de frota não possui coluna própria no schema,
            # então é opcionalmente incorporado ao modelo entre colchetes.
            frota_num = ent_frota.get().strip()
            modelo_final = f"{m} [F:{frota_num}]" if frota_num else m

            if self.db.execute_query(
                "INSERT OR IGNORE INTO veiculos (placa,modelo,tipo,status) VALUES (?,?,?,?)",
                (p, modelo_final, tipo_cb.get(), "Ativo")):
                messagebox.showinfo("Sucesso", f"{campo} {p} cadastrado!")
                self.show_veiculos()
            else:
                messagebox.showerror("Erro", f"{campo} já existe.")

        ctk.CTkButton(form, text="💾 SALVAR", fg_color=C_ACCENT, height=38,
                      command=salvar).grid(row=1,column=5,padx=16,pady=(0,16))

        # ── Lista ─────────────────────────────────────────────────
        lc = card(self.container)
        lc.pack(fill="both", expand=True, pady=8, padx=4)
        ctk.CTkLabel(lc, text="Veículos Cadastrados",
                     font=ctk.CTkFont("Arial",12,"bold"),
                     text_color=C_MUTED).pack(anchor="w", padx=16, pady=(12,4))

        sty  = style_tree("Veic")
        cols = ("Placa / ID","Modelo","Tipo","Status")
        ft   = ctk.CTkFrame(lc, fg_color="transparent")
        ft.pack(fill="both", expand=True, padx=12, pady=(0,6))
        tree = ttk.Treeview(ft, columns=cols, show="headings", height=12, style=sty)
        vsb  = ctk.CTkScrollbar(ft, command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=170, anchor="center")
        tree.pack(fill="both", expand=True)

        def reload_tree():
            tree.delete(*tree.get_children())
            df_v = self.db.get_dataframe(
                "SELECT placa,modelo,tipo,status FROM veiculos ORDER BY tipo,placa")
            for _, row in df_v.iterrows():
                tree.insert("","end", values=tuple(row))

        reload_tree()

        btn_row = ctk.CTkFrame(lc, fg_color="transparent")
        btn_row.pack(fill="x", padx=12, pady=(0,12))

        def editar():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Atenção","Selecione um veículo."); return
            vals = tree.item(sel[0])["values"]
            open_edit_veiculo(self, self.db,
                              vals[0], vals[1], vals[2], vals[3], reload_tree)

        def excluir():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Atenção","Selecione um veículo."); return
            placa = tree.item(sel[0])["values"][0]
            tipo  = tree.item(sel[0])["values"][2]
            campo = label_identificador(tipo)
            if not messagebox.askyesno("Confirmar",
                f"Excluir {campo} {placa}?\n\n"
                "Os registros de abastecimento não serão apagados."): return
            if self.db.delete_veiculo(placa):
                messagebox.showinfo("Excluído", f"{campo} {placa} removido.")
                reload_tree()
            else:
                messagebox.showerror("Erro","Não foi possível excluir.")

        ctk.CTkButton(btn_row, text="✏️  Editar selecionado",
                      fg_color=C_ACCENT, height=36,
                      font=ctk.CTkFont("Arial",11,"bold"),
                      command=editar).pack(side="left", padx=(0,8))
        ctk.CTkButton(btn_row, text="🗑️  Excluir selecionado",
                      fg_color=C_DANGER, height=36,
                      font=ctk.CTkFont("Arial",11,"bold"),
                      command=excluir).pack(side="left")

    # =============================================================
    # CONDUTORES
    # =============================================================
    def show_condutores(self):
        self.clear_container()
        self.render_header("CADASTRO DE CONDUTORES")

        top = card(self.container); top.pack(fill="x", pady=8, padx=4)
        nome_e = ctk.CTkEntry(top, placeholder_text="Nome completo",
                               width=400, height=38)
        nome_e.pack(side="left", padx=20, pady=20)

        def salvar():
            n = nome_e.get().upper().strip()
            if n and self.db.execute_query(
                "INSERT OR IGNORE INTO condutores (nome,data_cadastro) VALUES (?,?)",
                (n, datetime.now().strftime("%Y-%m-%d"))):
                messagebox.showinfo("Sucesso", f"{n} cadastrado!")
                nome_e.delete(0,"end")
                self.show_condutores()
            else:
                messagebox.showerror("Erro","Já existe ou campo vazio.")

        ctk.CTkButton(top, text="➕ ADICIONAR", fg_color=C_SUCCESS,
                      height=38, command=salvar).pack(side="left", padx=10)

        df_c = self.db.get_dataframe(
            "SELECT nome,data_cadastro FROM condutores ORDER BY nome")
        lc = card(self.container); lc.pack(fill="both", expand=True, pady=8, padx=4)
        sty = style_tree("Cond")
        tree = ttk.Treeview(lc, columns=("Nome","Data"),
                             show="headings", style=sty)
        tree.heading("Nome",text="👤  Nome"); tree.column("Nome",width=400)
        tree.heading("Data",text="Cadastrado em")
        tree.column("Data",width=140,anchor="center")
        for _,row in df_c.iterrows():
            tree.insert("","end",values=(row["nome"],row["data_cadastro"]))
        tree.pack(fill="both", expand=True, padx=12, pady=12)
