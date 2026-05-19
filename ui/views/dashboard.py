# =================================================================
# UI/VIEWS/DASHBOARD.PY — Dashboard central com KPIs e gráficos
# =================================================================
import pandas as pd
import matplotlib.pyplot as plt
import customtkinter as ctk
from datetime import datetime

from config import (C_BG, C_SURFACE, C_ACCENT, C_SUCCESS,
                    C_WARNING, C_DANGER, C_TEXT, C_MUTED, C_BORDER)
from ui.widgets import card, kpi_card, embed_chart


class DashboardView:

    def show_dashboard(self):
        self.clear_container()
        self.render_header("DASHBOARD CENTRAL",
                           "Visão consolidada · use os filtros para ajustar o período")

        df_all = self.db.get_dataframe("SELECT * FROM registros")
        if df_all.empty:
            self.show_empty_state(); return

        self.render_filter_bar(on_apply=self.show_dashboard)

        df = self._get_filtered_df()
        if df.empty:
            ctk.CTkLabel(self.container,
                         text="Nenhum registro no período selecionado.",
                         font=ctk.CTkFont("Arial",16), text_color=C_MUTED).pack(pady=40)
            return

        # BUG FIX: datas inválidas (NaT) chegam aqui após o pd.to_datetime
        # com errors="coerce" no _get_filtered_df. Se incluídas no groupby,
        # to_period("M") levanta NaTType errors no matplotlib. Filtra antes.
        df = df.dropna(subset=["data"])

        # ── KPIs ─────────────────────────────────────────────────
        kpi_row = ctk.CTkFrame(self.container, fg_color="transparent")
        kpi_row.pack(fill="x", pady=(0,14))

        total_val = df["valor"].sum()
        total_vol = df["quantidade"].sum()
        n_placas  = df["placa"].nunique()
        media_pl  = total_val / total_vol if total_vol > 0 else 0

        now       = datetime.now()
        mes_atual = df[df["data"].dt.month == now.month]["valor"].sum()
        mes_ant   = df[df["data"].dt.month == (now.month - 1 or 12)]["valor"].sum()
        if mes_ant > 0:
            pct = (mes_atual - mes_ant) / mes_ant * 100
            delta_txt = (f"▲ +{pct:.1f}% vs mês ant." if mes_atual > mes_ant
                         else f"▼ {pct:.1f}% vs mês ant.")
        else:
            delta_txt = ""

        kpi_card(kpi_row,"INVESTIMENTO",    f"R$ {total_val:,.2f}", 0, C_ACCENT,  delta_txt)
        kpi_card(kpi_row,"VOLUME",          f"{total_vol:,.0f} L",  1, C_SUCCESS, "")
        kpi_card(kpi_row,"FROTA ATIVA",     f"{n_placas} Unid.",    2, "#8B5CF6", "")
        kpi_card(kpi_row,"PREÇO MÉDIO / L", f"R$ {media_pl:.3f}",   3, C_WARNING, "")

        # ── Scroll com gráficos ───────────────────────────────────
        scroll = ctk.CTkScrollableFrame(self.container, fg_color="transparent",
                                        scrollbar_button_color=C_BORDER)
        scroll.pack(fill="both", expand=True)

        # --- Evolução mensal + pizza ---
        r1 = ctk.CTkFrame(scroll, fg_color="transparent")
        r1.pack(fill="x", pady=(0,10))
        r1.columnconfigure(0, weight=3); r1.columnconfigure(1, weight=1)

        card_evol = card(r1); card_evol.grid(row=0,column=0,sticky="nsew",padx=(0,8))
        card_pie  = card(r1); card_pie.grid(row=0,column=1,sticky="nsew")

        monthly = df.groupby(df["data"].dt.to_period("M"))["valor"].sum()
        monthly.index = monthly.index.to_timestamp()
        fig1, ax1 = plt.subplots(figsize=(9,3.2), dpi=100)
        fig1.patch.set_facecolor(C_SURFACE); ax1.set_facecolor(C_SURFACE)
        ax1.fill_between(monthly.index, monthly.values, color=C_ACCENT, alpha=0.18)
        ax1.plot(monthly.index, monthly.values, color=C_ACCENT, lw=2.5, marker="o", ms=5)
        for x, y in zip(monthly.index, monthly.values):
            ax1.annotate(f"R${y/1000:.1f}k", (x,y),
                         textcoords="offset points", xytext=(0,8),
                         ha="center", fontsize=7.5, color=C_TEXT)
        ax1.set_title("Evolução Financeira Mensal", color=C_TEXT,
                      fontsize=12, pad=10, loc="left")
        ax1.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda v,_: f"R${v/1000:.0f}k"))
        ax1.grid(True, alpha=0.3); fig1.tight_layout(pad=1.5)
        embed_chart(card_evol, fig1)

        cat_data = df.groupby("categoria")["valor"].sum()
        fig2, ax2 = plt.subplots(figsize=(4,3.2), dpi=100)
        fig2.patch.set_facecolor(C_SURFACE); ax2.set_facecolor(C_SURFACE)
        clrs = [C_ACCENT, C_DANGER, C_WARNING, C_SUCCESS][:len(cat_data)]
        wedges, texts, autotexts = ax2.pie(
            cat_data, labels=cat_data.index, autopct="%1.0f%%",
            colors=clrs, startangle=90,
            wedgeprops={"edgecolor": C_SURFACE, "linewidth":2})
        for t in texts:     t.set_color(C_MUTED); t.set_fontsize(8)
        for t in autotexts: t.set_color("white"); t.set_fontsize(9); t.set_fontweight("bold")
        ax2.set_title("Por Categoria", color=C_TEXT, fontsize=11, pad=6, loc="left")
        fig2.tight_layout(pad=1.2)
        embed_chart(card_pie, fig2)

        # --- Top 10 veículos ---
        card_top = card(scroll); card_top.pack(fill="x", pady=(0,10))
        top10 = df.groupby("placa")["valor"].sum().sort_values().tail(10)
        fig3, ax3 = plt.subplots(figsize=(12,3.5), dpi=100)
        fig3.patch.set_facecolor(C_SURFACE); ax3.set_facecolor(C_SURFACE)
        bar_c = [C_DANGER if v==top10.max() else C_ACCENT for v in top10.values]
        bars  = ax3.barh(top10.index, top10.values, color=bar_c,
                         height=0.55, edgecolor=C_SURFACE)
        ax3.set_title("Top Veículos por Custo Total", color=C_TEXT,
                      fontsize=12, pad=10, loc="left")
        ax3.xaxis.set_major_formatter(
            plt.FuncFormatter(lambda v,_: f"R${v:,.0f}"))
        for bar in bars:
            w = bar.get_width()
            ax3.text(w*1.005, bar.get_y()+bar.get_height()/2,
                     f"R${w:,.0f}", va="center", fontsize=8, color=C_TEXT)
        ax3.set_xlim(0, top10.max()*1.15); fig3.tight_layout(pad=1.5)
        embed_chart(card_top, fig3)

        # --- KM/L + empilhado ---
        r2 = ctk.CTkFrame(scroll, fg_color="transparent")
        r2.pack(fill="x", pady=(0,16))
        r2.columnconfigure(0, weight=1); r2.columnconfigure(1, weight=1)

        card_kml = card(r2); card_kml.grid(row=0,column=0,sticky="nsew",padx=(0,8))
        card_stk = card(r2); card_stk.grid(row=0,column=1,sticky="nsew")

        medias = []
        for p in df["placa"].unique():
            t = df[df["placa"]==p].sort_values("horimetro")
            if len(t)>1 and t["quantidade"].sum()>0:
                kml = (t["horimetro"].max()-t["horimetro"].min())/t["quantidade"].sum()
                medias.append({"placa":p,"kml":round(kml,2)})
        df_kml = (pd.DataFrame(medias).sort_values("kml",ascending=False).head(10)
                  if medias else pd.DataFrame())

        fig4, ax4 = plt.subplots(figsize=(6,3.6), dpi=100)
        fig4.patch.set_facecolor(C_SURFACE); ax4.set_facecolor(C_SURFACE)
        if not df_kml.empty:
            bc = [C_SUCCESS if v>=df_kml["kml"].median() else C_WARNING
                  for v in df_kml["kml"]]
            ax4.bar(df_kml["placa"], df_kml["kml"], color=bc,
                    width=0.6, edgecolor=C_SURFACE)
            for i,(_, r) in enumerate(df_kml.iterrows()):
                ax4.text(i, r["kml"]+0.05, f"{r['kml']:.1f}",
                         ha="center", fontsize=7.5, color=C_TEXT)
            ax4.tick_params(axis="x", labelrotation=40, labelsize=8)
        ax4.set_title("Eficiência por Veículo (km/L)", color=C_TEXT,
                      fontsize=11, pad=8, loc="left")
        ax4.set_ylabel("km/L", color=C_MUTED, fontsize=9)
        fig4.tight_layout(pad=1.5)
        embed_chart(card_kml, fig4)

        # BUG FIX: mesmo dropna aplicado ao pivot mensal — NaT em to_period
        # dentro do unstack() também causava KeyError/NaTType crash.
        df_piv = df.groupby(
            [df["data"].dt.to_period("M"),"categoria"])["valor"].sum().unstack(fill_value=0)
        df_piv.index = df_piv.index.to_timestamp()
        fig5, ax5 = plt.subplots(figsize=(6,3.6), dpi=100)
        fig5.patch.set_facecolor(C_SURFACE); ax5.set_facecolor(C_SURFACE)
        if not df_piv.empty:
            bottoms = None
            for col, clr in [("ABASTECIMENTO",C_ACCENT),("MANUTENÇÃO",C_DANGER)]:
                if col in df_piv.columns:
                    ax5.bar(df_piv.index, df_piv[col], label=col, color=clr,
                            alpha=0.85, width=20, bottom=bottoms)
                    bottoms = df_piv[col] if bottoms is None else bottoms+df_piv[col]
            ax5.legend(fontsize=8, loc="upper left",
                       framealpha=0.2, labelcolor=C_TEXT)
            ax5.yaxis.set_major_formatter(
                plt.FuncFormatter(lambda v,_: f"R${v/1000:.0f}k"))
        ax5.set_title("Custo Mensal Empilhado", color=C_TEXT,
                      fontsize=11, pad=8, loc="left")
        fig5.tight_layout(pad=1.5)
        embed_chart(card_stk, fig5)
