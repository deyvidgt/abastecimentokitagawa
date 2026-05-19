# UI/VIEWS/REGISTROS.PY — Pesquisa, edição e exclusão de registros
from datetime import datetime
import customtkinter as ctk
from tkinter import ttk, messagebox
# BUG FIX: removido "filedialog" — importado mas nunca utilizado neste módulo.
# Importações desnecessárias aumentam o tempo de carga e causam confusão.

from config import C_ACCENT, C_DANGER, C_MUTED, C_SURFACE, C_BORDER
from ui.widgets import card, style_tree
from ui.dialogs import open_edit_registro
# BUG FIX: movido para o topo do módulo. Antes estava dentro do corpo de
# show_novo_registro(), causando re-importação a cada vez que o usuário
# navegava para essa tela. Python faz cache de imports, mas a instrução
# "from etl import ProcessorETL" dentro de um método é executada toda vez,
# gerando overhead desnecessário de lookup em sys.modules.
from etl import ProcessorETL


class RegistrosView:

    def show_registros(self):
        self.clear_container()
        self.render_header("REGISTROS","Pesquise, edite ou exclua lançamentos")

        bar = card(self.container); bar.pack(fill="x", pady=(0,10))
        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=10)

        ctk.CTkLabel(inner,text="🔍 Placa/ID:",
                     font=ctk.CTkFont("Arial",11,"bold"),
                     text_color=C_MUTED).pack(side="left",padx=(0,6))
        busca_placa = ctk.CTkEntry(inner,width=140,height=34,
                                    placeholder_text="ex: ABC1234")
        busca_placa.pack(side="left",padx=(0,8))

        ctk.CTkLabel(inner,text="Produto:",font=ctk.CTkFont("Arial",11,"bold"),
                     text_color=C_MUTED).pack(side="left",padx=(0,6))
        busca_prod = ctk.CTkEntry(inner,width=140,height=34,
                                   placeholder_text="ex: DIESEL")
        busca_prod.pack(side="left",padx=(0,8))

        ctk.CTkLabel(inner,text="De:",font=ctk.CTkFont("Arial",11,"bold"),
                     text_color=C_MUTED).pack(side="left",padx=(0,4))
        busca_ini = ctk.CTkEntry(inner,width=106,height=34,
                                  placeholder_text="DD-MM-AAAA")
        busca_ini.pack(side="left",padx=(0,4))

        ctk.CTkLabel(inner,text="Até:",font=ctk.CTkFont("Arial",11),
                     text_color=C_MUTED).pack(side="left",padx=(0,4))
        busca_fim = ctk.CTkEntry(inner,width=106,height=34,
                                  placeholder_text="DD-MM-AAAA")
        busca_fim.pack(side="left",padx=(0,10))

        lbl_total = ctk.CTkLabel(inner,text="",
                                  font=ctk.CTkFont("Arial",10),text_color=C_MUTED)
        lbl_total.pack(side="right")

        ct = card(self.container); ct.pack(fill="both", expand=True)
        cols = ("ID","Data","Placa / ID","Produto","Condutor",
                "Valor R$","Litros","Horímetro","Categoria")
        sty  = style_tree("Reg")
        ft   = ctk.CTkFrame(ct, fg_color="transparent")
        ft.pack(fill="both", expand=True, padx=10, pady=(6,4))
        tree = ttk.Treeview(ft, columns=cols, show="headings", style=sty)
        vsb  = ctk.CTkScrollbar(ft, command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right",fill="y")
        for col,w in zip(cols,[50,90,100,180,160,90,70,90,110]):
            tree.heading(col,text=col); tree.column(col,width=w,anchor="center")
        tree.pack(fill="both", expand=True)

        def refresh(*_):
            placa_f = busca_placa.get().strip().upper()
            prod_f  = busca_prod.get().strip().upper()
            ini_raw = busca_ini.get().strip()
            fim_raw = busca_fim.get().strip()
            sql  = ("SELECT id,data,placa,produto,responsavel,valor,quantidade,"
                    "horimetro,categoria FROM registros WHERE 1=1")
            prms = []
            if placa_f:
                sql += " AND UPPER(placa) LIKE ?"
                prms.append(f"%{placa_f}%")
            if prod_f:
                sql += " AND UPPER(produto) LIKE ?"
                prms.append(f"%{prod_f}%")
            try:
                if ini_raw:
                    sql += " AND data >= ?"
                    prms.append(datetime.strptime(
                        ini_raw.replace("/","-"),"%d-%m-%Y").strftime("%Y-%m-%d"))
                if fim_raw:
                    sql += " AND data <= ?"
                    prms.append(datetime.strptime(
                        fim_raw.replace("/","-"),"%d-%m-%Y").strftime("%Y-%m-%d"))
            except ValueError:
                pass
            sql += " ORDER BY data DESC, id DESC LIMIT 500"
            df = self.db.get_dataframe(sql, tuple(prms))
            tree.delete(*tree.get_children())
            for _, row in df.iterrows():
                tree.insert("","end", values=(
                    row["id"], row["data"], row["placa"], row["produto"],
                    row["responsavel"], f"{row['valor']:.2f}",
                    f"{row['quantidade']:.1f}",
                    f"{row['horimetro']:.0f}", row["categoria"]))
            lbl_total.configure(text=f"{len(df)} registro(s)")

        for w in [busca_placa, busca_prod, busca_ini, busca_fim]:
            w.bind("<KeyRelease>", refresh)

        btn_row = ctk.CTkFrame(ct, fg_color="transparent")
        btn_row.pack(fill="x", padx=10, pady=(0,10))

        def editar():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Atenção","Selecione um registro."); return
            open_edit_registro(self,
                               self.db,
                               int(tree.item(sel[0])["values"][0]),
                               refresh)

        def excluir():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Atenção","Selecione um registro."); return
            reg_id = int(tree.item(sel[0])["values"][0])
            if not messagebox.askyesno("Confirmar",
                f"Excluir registro #{reg_id}?\nEsta ação não pode ser desfeita."): return
            if self.db.delete_registro(reg_id):
                messagebox.showinfo("Excluído",f"Registro #{reg_id} removido.")
                refresh()
            else:
                messagebox.showerror("Erro","Não foi possível excluir.")

        ctk.CTkButton(btn_row,text="✏️  Editar",fg_color=C_ACCENT,height=36,
                      font=ctk.CTkFont("Arial",11,"bold"),
                      command=editar).pack(side="left",padx=(0,8))
        ctk.CTkButton(btn_row,text="🗑️  Excluir",fg_color=C_DANGER,height=36,
                      font=ctk.CTkFont("Arial",11,"bold"),
                      command=excluir).pack(side="left")
        refresh()

    # =============================================================
    # NOVO REGISTRO MANUAL
    # =============================================================
    def show_novo_registro(self):
        self.clear_container()
        self.render_header("LANÇAMENTO MANUAL",
                           "Registre um abastecimento ou manutenção")

        form = card(self.container)
        form.pack(pady=8, padx=4, fill="both", expand=True)

        lv = self.db.get_dataframe("SELECT placa FROM veiculos")["placa"].tolist()
        lc = self.db.get_dataframe("SELECT nome FROM condutores")["nome"].tolist()

        def lbl(text,r,col):
            ctk.CTkLabel(form,text=text,font=ctk.CTkFont("Arial",11),
                         text_color=C_MUTED).grid(row=r,column=col,padx=20,pady=(14,2),sticky="w")
        def ent(r,col,ph="",val=""):
            e = ctk.CTkEntry(form,width=300,height=38,placeholder_text=ph)
            if val: e.insert(0,val)
            e.grid(row=r,column=col,padx=20,pady=(0,4)); return e

        lbl("Data (DD-MM-AAAA)",0,0)
        data_e = ent(1,0,val=datetime.now().strftime("%d-%m-%Y"))
        lbl("Veículo (Placa)",0,1)
        veic_c = ctk.CTkComboBox(form,values=lv or ["—"],width=300,height=38)
        veic_c.grid(row=1,column=1,padx=20)
        lbl("Condutor",2,0)
        cond_c = ctk.CTkComboBox(form,values=lc or ["—"],width=300,height=38)
        cond_c.grid(row=3,column=0,padx=20)
        lbl("Produto/Combustível",2,1)
        prod_c = ctk.CTkComboBox(form,
            values=["DIESEL S10","DIESEL S500","GASOLINA","ETANOL",
                    "ARLA 32","ÓLEO","FILTRO","PNEU","OUTRO"],
            width=300,height=38)
        prod_c.grid(row=3,column=1,padx=20)
        lbl("Quantidade (L)",4,0); qtd_e=ent(5,0,"0.00")
        lbl("Valor Total (R$)",4,1); val_e=ent(5,1,"0.00")
        lbl("Horímetro / KM",6,0); hor_e=ent(7,0,"0.0")

        def confirmar():
            try:
                raw = data_e.get().strip().replace("/","-")
                data_str = datetime.strptime(raw,"%d-%m-%Y").strftime("%Y-%m-%d")
                dados = (
                    data_str, prod_c.get().upper(), cond_c.get().upper(),
                    veic_c.get().upper(), "MANUAL",
                    float(val_e.get().replace(",",".")),
                    float(qtd_e.get().replace(",",".")),
                    float(hor_e.get().replace(",",".")),
                    ProcessorETL.identify_category(prod_c.get()),
                    "LANÇAMENTO MANUAL",
                    f"MAN-{datetime.now().timestamp()}-{veic_c.get()}")
                if self.db.execute_query("""
                    INSERT INTO registros
                    (data,produto,responsavel,placa,frota,valor,quantidade,
                     horimetro,categoria,arquivo_origem,hash_verificacao)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)""", dados):
                    messagebox.showinfo("Sucesso","Registro salvo!")
                    self.show_dashboard()
                else:
                    messagebox.showerror("Erro","Registro duplicado ou inválido.")
            except ValueError:
                messagebox.showerror("Erro",
                    "Data inválida (use DD-MM-AAAA) ou campos numéricos incorretos.")

        ctk.CTkButton(form, text="➕  FINALIZAR LANÇAMENTO",
                      fg_color="#22C55E", hover_color="#16A34A", height=50,
                      font=ctk.CTkFont("Arial",15,"bold"), corner_radius=10,
                      command=confirmar).grid(row=8,column=0,columnspan=2,
                                              pady=36,padx=20,sticky="ew")
