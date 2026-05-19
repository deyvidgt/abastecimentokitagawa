# =================================================================
# UI/WIDGETS.PY — Componentes visuais reutilizáveis
# =================================================================
import customtkinter as ctk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from config import (C_BG, C_SURFACE, C_BORDER, C_TEXT, C_MUTED,
                    C_ACCENT, C_SUCCESS, C_WARNING, C_DANGER)


def make_separator(parent, pady=5):
    ctk.CTkFrame(parent, height=1, fg_color=C_BORDER).pack(fill="x", pady=pady)


def card(parent, **kw):
    return ctk.CTkFrame(parent, fg_color=C_SURFACE, corner_radius=12,
                        border_width=1, border_color=C_BORDER, **kw)


def style_tree(name):
    s = ttk.Style()
    s.configure(f"{name}.Treeview",
                background=C_SURFACE, foreground=C_TEXT,
                fieldbackground=C_SURFACE, rowheight=26,
                font=("Arial", 10))
    s.configure(f"{name}.Treeview.Heading",
                background=C_BG, foreground=C_MUTED,
                font=("Arial", 9, "bold"), relief="flat")
    s.map(f"{name}.Treeview",
          background=[("selected", C_ACCENT)])
    return f"{name}.Treeview"


def embed_chart(parent, fig):
    cv = FigureCanvasTkAgg(fig, master=parent)
    cv.draw()
    cv.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    plt.close(fig)


def kpi_card(master, label, value, col, color, delta=""):
    c = card(master)
    c.grid(row=0, column=col, padx=8, sticky="nsew")
    c.grid_propagate(False)
    c.configure(height=110)
    master.grid_columnconfigure(col, weight=1)
    ctk.CTkFrame(c, width=4, fg_color=color, corner_radius=2).pack(
        side="left", fill="y", padx=(0, 12))
    inner = ctk.CTkFrame(c, fg_color="transparent")
    inner.pack(side="left", fill="both", expand=True, pady=16, padx=(0, 16))
    ctk.CTkLabel(inner, text=label,
                 font=ctk.CTkFont("Arial", 10, "bold"),
                 text_color=C_MUTED).pack(anchor="w")
    ctk.CTkLabel(inner, text=value,
                 font=ctk.CTkFont("Arial", 22, "bold"),
                 text_color=C_TEXT).pack(anchor="w", pady=(4, 0))
    if delta:
        # BUG FIX: a cor do delta era sempre C_SUCCESS (verde), mesmo quando
        # o texto continha "▼" indicando queda. Um delta negativo deve aparecer
        # em vermelho (C_DANGER) para comunicar corretamente ao usuário.
        # A detecção é feita pelo caractere ▼ presente na string formatada
        # em dashboard.py (ex: "▼ -15.3% vs mês ant.").
        delta_color = C_DANGER if "▼" in delta else C_SUCCESS
        ctk.CTkLabel(inner, text=delta,
                     font=ctk.CTkFont("Arial", 10),
                     text_color=delta_color).pack(anchor="w")
