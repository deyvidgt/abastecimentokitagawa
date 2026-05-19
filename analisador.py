"""
SISTEMA ABASTECIMENTO ERP PRO v11.0 - GESTÃO E INTELIGÊNCIA DE FROTA
---------------------------------------------------------------------
Ponto de entrada único — garante instância única via mutex nomeado
(Windows: CreateMutex / Linux/Mac: arquivo de lock em /tmp).
"""

import sys
import logging

# =================================================================
# INSTÂNCIA ÚNICA
# =================================================================
_MUTEX_NAME = "SistemaAbastecimentoERP_SingleInstance_v11"

if sys.platform == "win32":
    import ctypes

    _mutex = ctypes.windll.kernel32.CreateMutexW(None, False, _MUTEX_NAME)
    _last_error = ctypes.windll.kernel32.GetLastError()
    ERROR_ALREADY_EXISTS = 183

    if _last_error == ERROR_ALREADY_EXISTS:
        import ctypes.wintypes
        _user32 = ctypes.windll.user32

        def _bring_to_front(hwnd, lParam):
            buf = ctypes.create_unicode_buffer(512)
            _user32.GetWindowTextW(hwnd, buf, 512)
            if _MUTEX_NAME[:20] in buf.value or "KITAGAWA" in buf.value:
                _user32.ShowWindow(hwnd, 9)
                _user32.SetForegroundWindow(hwnd)
                return False
            return True

        EnumWindowsProc = ctypes.WINFUNCTYPE(
            ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)
        _user32.EnumWindows(EnumWindowsProc(_bring_to_front), 0)

        import tkinter as tk
        from tkinter import messagebox
        _r = tk.Tk(); _r.withdraw()
        messagebox.showwarning(
            "Já em execução",
            "O Sistema de Abastecimento já está aberto.\n"
            "Verifique a barra de tarefas.")
        _r.destroy()
        sys.exit(0)

else:
    import os, fcntl, atexit

    _LOCK_FILE = f"/tmp/{_MUTEX_NAME}.lock"
    _lock_fp   = open(_LOCK_FILE, "w")
    try:
        fcntl.flock(_lock_fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        import tkinter as tk
        from tkinter import messagebox
        _r = tk.Tk(); _r.withdraw()
        messagebox.showwarning(
            "Já em execução",
            "O Sistema de Abastecimento já está aberto.\n"
            "Verifique a barra de tarefas.")
        _r.destroy()
        sys.exit(0)

    def _release_lock():
        try:
            fcntl.flock(_lock_fp, fcntl.LOCK_UN)
            _lock_fp.close()
            os.unlink(_LOCK_FILE)
        except Exception:
            pass

    atexit.register(_release_lock)


# =================================================================
# INICIALIZAÇÃO DA APLICAÇÃO
# =================================================================
if __name__ == "__main__":
    try:
        from database import DataEngine
        from login    import LoginWindow
        from ui.app   import ERP_Mutima

        # 1. Inicializa o banco (cria tabelas + usuário admin se necessário)
        db = DataEngine()

        # 2. Exibe tela de login — bloqueia até fechar
        login = LoginWindow(db)
        login.mainloop()

        # 3. Só abre o ERP se o login foi bem-sucedido
        if login.login_ok:
            app = ERP_Mutima()
            app.mainloop()
        else:
            logging.info("Login cancelado — sistema encerrado.")

    except Exception as e:
        logging.critical(f"Falha crítica: {e}", exc_info=True)
        raise
