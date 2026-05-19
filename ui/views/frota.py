# UI/VIEWS/FROTA.PY
import pandas as pd
import customtkinter as ctk
from tkinter import ttk
from config import C_ACCENT, C_SUCCESS, C_WARNING, C_DANGER, C_TEXT, C_MUTED, C_BG
from ui.widgets import card, style_tree


class FrotaView:

    def show_frota(self):
        self.clear_container()
        self.render_header("CONTROLE DE FROTA","Histórico e eficiência por veículo")

        df_placas = self.db.get_dataframe(
            "SELECT DISTINCT placa FROM registros ORDER BY placa")
        if df_placas.empty:
            self.show_empty_state(); return

        df_total = self.db.get_dataframe("SELECT * FROM registros")
        for col in ["valor","quantidade","horimetro"]:
            df_total[col] = pd.to_numeric(df_total[col], errors="coerce").fillna(0)

        scroll = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        sty = style_tree("Frota")

        for placa in df_placas["placa"].unique():
            v       = df_total[df_total["placa"]==placa].sort_values("horimetro")
            custo   = v["valor"].sum()
            ltrs    = v["quantidade"].sum()
            diff_km = v["horimetro"].max()-v["horimetro"].min() if len(v)>1 else 0
            kml     = diff_km/ltrs if ltrs > 0 else 0
            cor_kml = C_SUCCESS if kml>10 else (C_WARNING if kml>5 else C_DANGER)

            c = card(scroll); c.pack(fill="x", pady=8, padx=4)
            h = ctk.CTkFrame(c, fg_color="transparent")
            h.pack(fill="x", padx=16, pady=(12,4))
            ctk.CTkLabel(h, text=f"🚛  {placa}",
                         font=ctk.CTkFont("Arial",18,"bold"),
                         text_color=C_TEXT).pack(side="left")

            sf = ctk.CTkFrame(h, fg_color="transparent")
            sf.pack(side="right")
            for lbl,val,clr in [("CUSTO",f"R$ {custo:,.2f}",C_ACCENT),
                                  ("LITROS",f"{ltrs:,.0f} L",C_SUCCESS),
                                  ("KM/L",f"{kml:.2f}",cor_kml)]:
                cf = ctk.CTkFrame(sf, fg_color=C_BG, corner_radius=8)
                cf.pack(side="left", padx=5)
                ctk.CTkLabel(cf,text=lbl,font=ctk.CTkFont("Arial",9),
                             text_color=C_MUTED).pack(padx=10,pady=(6,0))
                ctk.CTkLabel(cf,text=val,font=ctk.CTkFont("Arial",13,"bold"),
                             text_color=clr).pack(padx=10,pady=(0,6))

            df_v = self.db.get_dataframe(
                "SELECT data,produto,valor,quantidade,horimetro,responsavel "
                "FROM registros WHERE placa=? ORDER BY data DESC",
                (placa,))

            # BUG FIX: df_v é uma query independente de df_total e não passa
            # por pd.to_numeric. Campos NULL do SQLite chegam como NaN (float),
            # e embora f"{nan:.2f}" não crash, exibe "nan" em vez de "0.00",
            # gerando dados ruins no Treeview. O fillna(0) garante exibição correta.
            for num_col in ["valor","quantidade","horimetro"]:
                df_v[num_col] = pd.to_numeric(
                    df_v[num_col], errors="coerce").fillna(0)

            cols = ("Data","Produto","Valor R$","Litros","Horímetro","Condutor")
            ft   = ctk.CTkFrame(c, fg_color="transparent")
            ft.pack(fill="x", padx=16, pady=(4,12))
            tree = ttk.Treeview(ft, columns=cols, show="headings",
                                height=min(len(df_v),6), style=sty)
            for col_name, w in zip(cols,[80,180,90,70,90,130]):
                tree.heading(col_name, text=col_name)
                tree.column(col_name, width=w, anchor="center")
            for _,row in df_v.iterrows():
                tree.insert("","end", values=(
                    row["data"],row["produto"],
                    f"{row['valor']:.2f}",f"{row['quantidade']:.1f}",
                    f"{row['horimetro']:.0f}",row["responsavel"]))
            tree.pack(fill="x")
