# =================================================================
# LOGIN.PY — Tela de autenticação com detector de CapsLock
# =================================================================
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import os
from PIL import Image

from config import (C_BG, C_SURFACE, C_BORDER, C_ACCENT,
                    C_TEXT, C_MUTED, C_WARNING, C_DANGER, C_SUCCESS,
                    CAMINHO_LOGO)


class LoginWindow(ctk.CTk):
    """
    Janela de login exibida antes do ERP principal.
    Autentica o usuário, detecta CapsLock em tempo real
    e oferece link para troca de senha.
    """

    def __init__(self, db):
        super().__init__()
        self.db            = db
        self.login_ok      = False   # flag lida pelo analisador.py
        self._caps_on      = False
        self._senha_visivel = False

        self.title("KITAGAWA — Login")
        self.geometry("480x600")
        self.resizable(False, False)
        self.configure(fg_color=C_BG)

        if os.path.exists("logo.ico"):
            self.iconbitmap("logo.ico")

        self._build_ui()
        self._check_capslock_loop()

        # Centraliza na tela
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - 480) // 2
        y = (self.winfo_screenheight() - 600) // 2
        self.geometry(f"480x600+{x}+{y}")

        # Enter confirma login
        self.bind("<Return>", lambda _: self._tentar_login())

    # ── Construção da UI ──────────────────────────────────────────
    def _build_ui(self):
        # Logo
        try:
            if os.path.exists(CAMINHO_LOGO):
                img = Image.open(CAMINHO_LOGO)
                self._img = ctk.CTkImage(img, size=(100, 100))
                ctk.CTkLabel(self, image=self._img, text="").pack(pady=(40, 8))
        except Exception:
            pass

        ctk.CTkLabel(self, text="KITAGAWA",
                     font=ctk.CTkFont("Arial", 22, "bold"),
                     text_color=C_TEXT).pack()
        ctk.CTkLabel(self, text="Sistema de Gestão de Abastecimento",
                     font=ctk.CTkFont("Arial", 11),
                     text_color=C_MUTED).pack(pady=(2, 32))

        # Card central
        card = ctk.CTkFrame(self, fg_color=C_SURFACE, corner_radius=16,
                             border_width=1, border_color=C_BORDER)
        card.pack(fill="x", padx=48)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=28, pady=28)

        # Usuário
        ctk.CTkLabel(inner, text="Usuário",
                     font=ctk.CTkFont("Arial", 11, "bold"),
                     text_color=C_MUTED).pack(anchor="w")
        self.ent_user = ctk.CTkEntry(inner, height=42, corner_radius=8,
                                      placeholder_text="Digite seu usuário",
                                      font=ctk.CTkFont("Arial", 13))
        self.ent_user.pack(fill="x", pady=(4, 14))

        # Senha
        ctk.CTkLabel(inner, text="Senha",
                     font=ctk.CTkFont("Arial", 11, "bold"),
                     text_color=C_MUTED).pack(anchor="w")

        senha_row = ctk.CTkFrame(inner, fg_color="transparent")
        senha_row.pack(fill="x", pady=(4, 0))

        self.ent_senha = ctk.CTkEntry(senha_row, height=42, corner_radius=8,
                                       show="●",
                                       placeholder_text="Digite sua senha",
                                       font=ctk.CTkFont("Arial", 13))
        self.ent_senha.pack(side="left", fill="x", expand=True)

        self.btn_eye = ctk.CTkButton(senha_row, text="👁", width=42, height=42,
                                      fg_color=C_BORDER, hover_color=C_ACCENT,
                                      corner_radius=8,
                                      font=ctk.CTkFont("Arial", 16),
                                      command=self._toggle_senha)
        self.btn_eye.pack(side="left", padx=(6, 0))

        # Aviso CapsLock
        self.lbl_caps = ctk.CTkLabel(inner, text="",
                                      font=ctk.CTkFont("Arial", 10, "bold"),
                                      text_color=C_WARNING)
        self.lbl_caps.pack(anchor="w", pady=(6, 0))

        # Botão entrar
        ctk.CTkButton(inner, text="ENTRAR", height=46, corner_radius=10,
                       fg_color=C_ACCENT, hover_color="#2563EB",
                       font=ctk.CTkFont("Arial", 14, "bold"),
                       command=self._tentar_login).pack(fill="x", pady=(20, 0))

        # Link alterar senha
        ctk.CTkButton(inner, text="🔑  Esqueci / alterar senha",
                       fg_color="transparent", hover_color=C_BORDER,
                       text_color=C_MUTED, font=ctk.CTkFont("Arial", 11),
                       height=32, command=self._abrir_alterar_senha).pack(pady=(10, 0))

    # ── Mostrar/ocultar senha ─────────────────────────────────────
    def _toggle_senha(self):
        self._senha_visivel = not self._senha_visivel
        self.ent_senha.configure(show="" if self._senha_visivel else "●")
        self.btn_eye.configure(text="🙈" if self._senha_visivel else "👁")

    # ── Detector de CapsLock (polling a cada 300 ms) ──────────────
    def _check_capslock_loop(self):
        """
        Verifica o estado do CapsLock a cada 300 ms.
        No Windows: usa GetKeyState via ctypes.
        No Linux/Mac: tenta via X11; fallback silencioso se indisponível.
        """
        caps = self._get_capslock_state()
        if caps != self._caps_on:
            self._caps_on = caps
            if caps:
                self.lbl_caps.configure(
                    text="⚠  CAPS LOCK ATIVADO — letras maiúsculas",
                    text_color=C_WARNING)
            else:
                self.lbl_caps.configure(text="")
        self.after(300, self._check_capslock_loop)

    @staticmethod
    def _get_capslock_state() -> bool:
        try:
            import ctypes
            return bool(ctypes.windll.user32.GetKeyState(0x14) & 0xFFFF)
        except Exception:
            pass
        try:
            import subprocess
            out = subprocess.check_output(
                ["xset", "q"], stderr=subprocess.DEVNULL).decode()
            return "Caps Lock:   on" in out
        except Exception:
            return False

    # ── Autenticação ──────────────────────────────────────────────
    def _tentar_login(self):
        usuario = self.ent_user.get().strip()
        senha   = self.ent_senha.get()

        if not usuario or not senha:
            messagebox.showwarning("Atenção", "Preencha usuário e senha.")
            return

        if self.db.verificar_login(usuario, senha):
            self.login_ok = True
            self.destroy()
        else:
            self.ent_senha.delete(0, "end")
            messagebox.showerror("Acesso negado",
                "Usuário ou senha incorretos.\n"
                "Verifique também se o CapsLock está ativado.")

    # ── Abrir tela de alteração de senha ──────────────────────────
    def _abrir_alterar_senha(self):
        from alterar_senha import AlterarSenhaWindow
        AlterarSenhaWindow(self, self.db)
