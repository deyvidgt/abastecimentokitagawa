# UI/VIEWS/CUSTOS.PY
import customtkinter as ctk
from tkinter import ttk
# BUG FIX: import pandas movido para o topo do módulo.
# Antes estava dentro do corpo de show_custos() (linha 14 do original),
# causando re-importação a cada vez que o usuário navegava para essa tela.
# O mesmo padrão já foi corrigido em registros.py e frota.py.
import pandas as pd
from config import C_TEXT, C_MUTED, C_WARNING
from ui.widgets import card, style_tree


class CustosView:

    def show_custos(self):
        self.clear_container()
        self.render_header("CENTRO DE CUSTOS","Manutenção e despesas por veículo")

        df = self.db.get_dataframe("SELECT * FROM registros ORDER BY data DESC")
        df["valor"] = pd.to_numeric(df["valor"], errors="coerce").fillna(0)

        summ = ctk.CTkFrame(self.container, fg_color="transparent")
        summ.pack(fill="x", pady=(0,12))
        for i,(cat,grp) in enumerate(df.groupby("categoria")):
            c = card(summ); c.grid(row=0,column=i,padx=8,sticky="nsew")
            summ.columnconfigure(i, weight=1)
            ctk.CTkLabel(c,text=cat,font=ctk.CTkFont("Arial",10,"bold"),
                         text_color=C_MUTED).pack(pady=(12,0))
            ctk.CTkLabel(c,text=f"R$ {grp['valor'].sum():,.2f}",
                         font=ctk.CTkFont("Arial",20,"bold"),
                         text_color=C_TEXT).pack(pady=(2,4))
            ctk.CTkLabel(c,text=f"{len(grp)} registros",
                         font=ctk.CTkFont("Arial",9),
                         text_color=C_MUTED).pack(pady=(0,12))

        c = card(self.container); c.pack(fill="both", expand=True)
        sty  = style_tree("Cost")
        cols = ("Data","Produto","Placa","Categoria","Valor R$","Responsável")
        tree = ttk.Treeview(c, columns=cols, show="headings", style=sty)
        vsb  = ctk.CTkScrollbar(c, command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        for col,w in zip(cols,[90,220,90,120,110,160]):
            tree.heading(col,text=col); tree.column(col,width=w,anchor="center")
        for _,row in df.iterrows():
            tree.insert("","end",
                values=(row["data"],row["produto"],row["placa"],
                        row["categoria"],f"{row['valor']:.2f}",row["responsavel"]),
                tags=("manut",) if row["categoria"]=="MANUTENÇÃO" else ())
        tree.tag_configure("manut", foreground=C_WARNING)
        tree.pack(fill="both", expand=True, padx=10, pady=10)
