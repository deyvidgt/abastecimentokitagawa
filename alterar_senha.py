# =================================================================
# ALTERAR_SENHA.PY — Editar ou resetar senha de usuário
# =================================================================
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from config import (C_BG, C_SURFACE, C_BORDER, C_ACCENT,
                    C_TEXT, C_MUTED, C_WARNING, C_DANGER, C_SUCCESS)


class AlterarSenhaWindow(ctk.CTkToplevel):
    """
    Janela modal para:
      - Usuário comum: informar senha atual + nova senha
      - Admin: resetar senha de qualquer usuário sem precisar da senha atual
    """

    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.title("Alterar / Resetar Senha")
        self.geometry("460x560")
        self.resizable(False, False)
        self.configure(fg_color=C_BG)
        self.attributes("-topmost", True)

        # Centraliza
        self.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width()  - 460) // 2
        py = parent.winfo_y() + (parent.winfo_height() - 560) // 2
        self.geometry(f"460x560+{px}+{py}")

        self._build_ui()
        self.grab_set()

    # ── UI ────────────────────────────────────────────────────────
    def _build_ui(self):
        ctk.CTkLabel(self, text="🔑  ALTERAR SENHA",
                     font=ctk.CTkFont("Arial", 18, "bold"),
                     text_color=C_ACCENT).pack(pady=(32, 4))
        ctk.CTkLabel(self, text="Preencha os campos abaixo para alterar a senha.",
                     font=ctk.CTkFont("Arial", 11),
                     text_color=C_MUTED).pack(pady=(0, 20))

        card = ctk.CTkFrame(self, fg_color=C_SURFACE, corner_radius=14,
                             border_width=1, border_color=C_BORDER)
        card.pack(fill="x", padx=36)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=24, pady=24)

        def lbl(text):
            ctk.CTkLabel(inner, text=text,
                         font=ctk.CTkFont("Arial", 11, "bold"),
                         text_color=C_MUTED).pack(anchor="w", pady=(10, 2))

        def ent(show=""):
            e = ctk.CTkEntry(inner, height=40, corner_radius=8,
                              show=show, font=ctk.CTkFont("Arial", 13))
            e.pack(fill="x")
            return e

        lbl("Usuário")
        self.ent_user = ent()

        lbl("Senha atual  (deixe em branco se for admin resetando)")
        self.ent_atual = ent(show="●")

        lbl("Nova senha")
        self.ent_nova = ent(show="●")

        lbl("Confirmar nova senha")
        self.ent_conf = ent(show="●")

        # Requisitos visuais de senha
        self.lbl_req = ctk.CTkLabel(inner,
            text="• Mínimo 6 caracteres",
            font=ctk.CTkFont("Arial", 10),
            text_color=C_MUTED)
        self.lbl_req.pack(anchor="w", pady=(6, 0))

        self.ent_nova.bind("<KeyRelease>", self._validar_forca)

        # Barra de força
        self.barra_frame = ctk.CTkFrame(inner, fg_color="transparent", height=6)
        self.barra_frame.pack(fill="x", pady=(4, 0))
        self.barra = ctk.CTkProgressBar(inner, height=6, corner_radius=3)
        self.barra.pack(fill="x", pady=(2, 0))
        self.barra.set(0)

        # Botões
        bf = ctk.CTkFrame(self, fg_color="transparent")
        bf.pack(fill="x", padx=36, pady=20)

        ctk.CTkButton(bf, text="💾  SALVAR NOVA SENHA",
                       fg_color=C_ACCENT, hover_color="#2563EB",
                       height=44, corner_radius=10,
                       font=ctk.CTkFont("Arial", 13, "bold"),
                       command=self._salvar).pack(fill="x", pady=(0, 8))

        ctk.CTkButton(bf, text="🔄  RESETAR PARA PADRÃO  (admin)",
                       fg_color=C_WARNING, hover_color="#D97706",
                       text_color="#1A1A1A",
                       height=40, corner_radius=10,
                       font=ctk.CTkFont("Arial", 12, "bold"),
                       command=self._resetar).pack(fill="x", pady=(0, 8))

        ctk.CTkButton(bf, text="Cancelar",
                       fg_color=C_SURFACE, border_width=1,
                       border_color=C_BORDER, height=38,
                       font=ctk.CTkFont("Arial", 12),
                       command=self.destroy).pack(fill="x")

    # ── Indicador de força da senha ───────────────────────────────
    def _validar_forca(self, _=None):
        senha = self.ent_nova.get()
        forca = 0
        dicas = []
        if len(senha) >= 6:  forca += 1
        else: dicas.append("mínimo 6 caracteres")
        if len(senha) >= 10: forca += 1
        if any(c.isupper() for c in senha): forca += 1
        else: dicas.append("maiúsculas")
        if any(c.isdigit() for c in senha): forca += 1
        else: dicas.append("números")
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in senha): forca += 1
        else: dicas.append("símbolos")

        cores  = ["#EF4444","#F59E0B","#EAB308","#22C55E","#10B981"]
        textos = ["Muito fraca","Fraca","Razoável","Boa","Forte"]
        idx    = min(forca, 4)

        self.barra.set(forca / 5)
        self.barra.configure(progress_color=cores[idx])
        dica = f"• {textos[idx]}" + (f" — adicione: {', '.join(dicas)}" if dicas else " ✔")
        self.lbl_req.configure(text=dica,
                                text_color=cores[idx])

    # ── Salvar nova senha ─────────────────────────────────────────
    def _salvar(self):
        usuario = self.ent_user.get().strip()
        atual   = self.ent_atual.get()
        nova    = self.ent_nova.get()
        conf    = self.ent_conf.get()

        if not usuario:
            messagebox.showwarning("Atenção", "Informe o usuário."); return
        if len(nova) < 6:
            messagebox.showwarning("Atenção", "A nova senha precisa ter no mínimo 6 caracteres."); return
        if nova != conf:
            messagebox.showerror("Erro", "A confirmação não coincide com a nova senha."); return

        # Se informou senha atual, valida antes de trocar
        if atual:
            if not self.db.verificar_login(usuario, atual):
                messagebox.showerror("Erro", "Senha atual incorreta."); return

        if self.db.alterar_senha(usuario, nova):
            messagebox.showinfo("Sucesso", f"Senha de '{usuario}' alterada com sucesso!")
            self.destroy()
        else:
            messagebox.showerror("Erro", f"Usuário '{usuario}' não encontrado.")

    # ── Resetar para senha padrão (admin) ─────────────────────────
    def _resetar(self):
        usuario = self.ent_user.get().strip()
        if not usuario:
            messagebox.showwarning("Atenção", "Informe o usuário a resetar."); return

        if not messagebox.askyesno("Confirmar Reset",
            f"Resetar a senha de '{usuario}' para o padrão '123456'?\n\n"
            "O usuário deverá trocar no próximo acesso."):
            return

        if self.db.alterar_senha(usuario, "123456"):
            messagebox.showinfo("Resetado",
                f"Senha de '{usuario}' resetada para: 123456\n"
                "Avise o usuário para trocar assim que logar.")
            self.destroy()
        else:
            messagebox.showerror("Erro", f"Usuário '{usuario}' não encontrado.")
