# =================================================================
# UI/DIALOGS.PY — Janelas modais do sistema
# =================================================================
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import customtkinter as ctk

from config import (C_BG, C_SURFACE, C_BORDER, C_ACCENT,
                    C_TEXT, C_MUTED, C_WARNING)

TIPOS_SEM_PLACA = {"Drone", "Máquina Agrícola", "Outro"}
TIPOS_VEICULO   = ["Caminhão","Caminhonete","Trator","Van","Leve",
                   "Máquina Agrícola","Drone","Outro"]


def label_identificador(tipo):
    return "Identificador" if tipo in TIPOS_SEM_PLACA else "Placa"


def gerar_id(tipo, db):
    prefixo = {"Drone":"DRONE","Máquina Agrícola":"MAQ","Outro":"EQUIP"}.get(tipo,"ID")
    existentes = db.get_dataframe(
        "SELECT placa FROM veiculos WHERE placa LIKE ?", (f"{prefixo}-%",))
    nums = []
    for p in existentes["placa"]:
        try: nums.append(int(p.split("-")[-1]))
        except ValueError: pass
    return f"{prefixo}-{max(nums, default=0)+1:03d}"


def _safe_float(value, default=0.0):
    """
    BUG FIX: converte valor do banco para float de forma segura.

    dict.get(chave, default) retorna o default apenas quando a chave
    NÃO existe. Como get_registro_by_id constrói o dict com TODAS as
    colunas, chaves de campos NULL existem — mas com valor None.
    Portanto reg.get('valor', 0) retorna None (não 0), e float(None)
    levanta TypeError ao abrir o diálogo de edição de qualquer registro
    que tenha campos numéricos nulos no banco.
    """
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


# =================================================================
# NovasPlacasDialog
# =================================================================
class NovasPlacasDialog(ctk.CTkToplevel):
    def __init__(self, parent, novas_placas: set):
        super().__init__(parent)
        self.title("Novas Placas Detectadas")
        self.geometry("620x520")
        self.configure(fg_color=C_SURFACE)
        self.attributes("-topmost", True)
        self.resizable(False, False)
        self.result = {}
        self._vars  = {}

        ctk.CTkLabel(self, text="⚠️  PLACAS NÃO CADASTRADAS",
                     font=ctk.CTkFont("Arial",15,"bold"),
                     text_color=C_WARNING).pack(pady=(24,4))
        ctk.CTkLabel(self,
            text=(f"{len(novas_placas)} placa(s) encontradas nos arquivos "
                  "não existem no sistema.\n"
                  "Selecione quais deseja cadastrar antes de importar."),
            font=ctk.CTkFont("Arial",11), text_color=C_MUTED).pack(pady=(0,12))

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", height=340)
        scroll.pack(fill="x", padx=20)
        tipos = TIPOS_VEICULO

        for placa in sorted(novas_placas):
            row_f = ctk.CTkFrame(scroll, fg_color=C_BG, corner_radius=8)
            row_f.pack(fill="x", pady=4)
            chk_var  = tk.BooleanVar(value=True)
            mod_var  = tk.StringVar(value="")
            tipo_var = tk.StringVar(value="Caminhão")
            self._vars[placa] = {"check":chk_var,"modelo":mod_var,"tipo":tipo_var}

            top_r = ctk.CTkFrame(row_f, fg_color="transparent")
            top_r.pack(fill="x", padx=12, pady=(8,4))
            ctk.CTkCheckBox(top_r, text=f"  🚛 {placa}", variable=chk_var,
                            font=ctk.CTkFont("Arial",13,"bold"), text_color=C_TEXT,
                            fg_color=C_ACCENT, checkmark_color="white").pack(side="left")

            bot_r = ctk.CTkFrame(row_f, fg_color="transparent")
            bot_r.pack(fill="x", padx=12, pady=(0,8))
            ctk.CTkEntry(bot_r, textvariable=mod_var,
                         placeholder_text="Modelo / descrição (opcional)",
                         width=280, height=32).pack(side="left", padx=(0,8))
            ctk.CTkComboBox(bot_r, values=tipos, variable=tipo_var,
                            width=160, height=32).pack(side="left")

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=16)
        ctk.CTkButton(btn_row, text="✅  Cadastrar selecionadas e continuar",
                      fg_color=C_ACCENT, height=42,
                      font=ctk.CTkFont("Arial",12,"bold"),
                      command=self._confirm).pack(side="left",expand=True,fill="x",padx=(0,8))
        ctk.CTkButton(btn_row, text="⏩  Pular e importar assim mesmo",
                      fg_color=C_SURFACE, border_width=1, border_color=C_BORDER,
                      height=42, font=ctk.CTkFont("Arial",12),
                      command=self._skip).pack(side="left",expand=True,fill="x")
        self.grab_set()
        self.wait_window()

    def _confirm(self):
        for placa, v in self._vars.items():
            if v["check"].get():
                self.result[placa] = {"modelo":v["modelo"].get() or placa,
                                      "tipo":v["tipo"].get(),"cadastrar":True}
        self.destroy()

    def _skip(self):
        self.result = {}
        self.destroy()


# =================================================================
# EditVeiculo
# =================================================================
def open_edit_veiculo(parent, db, placa_orig, modelo_orig,
                      tipo_orig, status_orig, callback):
    win = ctk.CTkToplevel(parent)
    win.title(f"Editar — {placa_orig}")
    win.geometry("500x420")
    win.configure(fg_color=C_SURFACE)
    win.attributes("-topmost", True)
    win.resizable(False, False)

    ctk.CTkLabel(win, text="✏️  EDITAR VEÍCULO / EQUIPAMENTO",
                 font=ctk.CTkFont("Arial",15,"bold"),
                 text_color=C_ACCENT).pack(pady=(22,14))

    form = ctk.CTkFrame(win, fg_color="transparent")
    form.pack(fill="x", padx=32)

    def rl(text, r):
        ctk.CTkLabel(form, text=text, font=ctk.CTkFont("Arial",11,"bold"),
                     text_color=C_MUTED).grid(row=r,column=0,sticky="w",pady=(12,2),padx=(0,12))

    rl("Tipo",0)
    cb_tipo = ctk.CTkComboBox(form, values=TIPOS_VEICULO, width=280, height=38)
    cb_tipo.set(tipo_orig if tipo_orig in TIPOS_VEICULO else TIPOS_VEICULO[0])
    cb_tipo.grid(row=1,column=0,sticky="w")

    lbl_id = ctk.CTkLabel(form, text=label_identificador(tipo_orig),
                           font=ctk.CTkFont("Arial",11,"bold"), text_color=C_MUTED)
    lbl_id.grid(row=2,column=0,sticky="w",pady=(12,2))

    id_frame = ctk.CTkFrame(form, fg_color="transparent")
    id_frame.grid(row=3,column=0,sticky="w")
    ent_placa = ctk.CTkEntry(id_frame, width=200, height=38)
    ent_placa.insert(0, placa_orig)
    ent_placa.pack(side="left")

    btn_gerar = ctk.CTkButton(id_frame, text="🔢 Gerar ID", width=100, height=38,
                               fg_color=C_WARNING, hover_color="#D97706",
                               font=ctk.CTkFont("Arial",10,"bold"))
    btn_gerar.pack(side="left", padx=(8,0))
    if tipo_orig not in TIPOS_SEM_PLACA:
        btn_gerar.pack_forget()

    def on_tipo(t):
        sem = t in TIPOS_SEM_PLACA
        lbl_id.configure(text="Identificador" if sem else "Placa")
        if sem: btn_gerar.pack(side="left", padx=(8,0))
        else:   btn_gerar.pack_forget()

    cb_tipo.configure(command=on_tipo)
    btn_gerar.configure(command=lambda: (
        ent_placa.delete(0,"end"),
        ent_placa.insert(0, gerar_id(cb_tipo.get(), db))))

    rl("Modelo / Descrição",4)
    ent_modelo = ctk.CTkEntry(form, width=280, height=38)
    ent_modelo.insert(0, modelo_orig)
    ent_modelo.grid(row=5,column=0,sticky="w")

    rl("Status",6)
    cb_status = ctk.CTkComboBox(form, values=["Ativo","Inativo","Manutenção"],
                                 width=280, height=38)
    cb_status.set(status_orig if status_orig in ["Ativo","Inativo","Manutenção"] else "Ativo")
    cb_status.grid(row=7,column=0,sticky="w")

    def salvar():
        nova  = ent_placa.get().upper().strip()
        mod   = ent_modelo.get().upper().strip()
        campo = label_identificador(cb_tipo.get())
        if not nova or not mod:
            messagebox.showwarning("Atenção", f"{campo} e Modelo são obrigatórios."); return
        if db.update_veiculo(placa_orig, nova, mod, cb_tipo.get(), cb_status.get()):
            messagebox.showinfo("Sucesso", f"{campo} atualizado para {nova}!")
            win.destroy(); callback()
        else:
            messagebox.showerror("Erro", f"Não foi possível salvar. {campo} já pode existir.")

    bf = ctk.CTkFrame(win, fg_color="transparent")
    bf.pack(fill="x", padx=32, pady=22)
    ctk.CTkButton(bf, text="💾  Salvar", fg_color=C_ACCENT, height=42,
                  font=ctk.CTkFont("Arial",13,"bold"),
                  command=salvar).pack(side="left",expand=True,fill="x",padx=(0,8))
    ctk.CTkButton(bf, text="Cancelar", fg_color=C_SURFACE,
                  border_width=1, border_color=C_BORDER, height=42,
                  command=win.destroy).pack(side="left",expand=True,fill="x")
    win.grab_set()


# =================================================================
# EditRegistro
# =================================================================
def open_edit_registro(parent, db, reg_id, callback):
    reg = db.get_registro_by_id(reg_id)
    if not reg:
        messagebox.showerror("Erro","Registro não encontrado."); return

    win = ctk.CTkToplevel(parent)
    win.title(f"Editar Registro #{reg_id}")
    win.geometry("560x520")
    win.configure(fg_color=C_SURFACE)
    win.attributes("-topmost", True)
    win.resizable(False, False)

    ctk.CTkLabel(win, text=f"✏️  EDITAR REGISTRO #{reg_id}",
                 font=ctk.CTkFont("Arial",15,"bold"),
                 text_color=C_ACCENT).pack(pady=(20,12))

    form = ctk.CTkFrame(win, fg_color="transparent")
    form.pack(fill="x", padx=28)

    lv = db.get_dataframe("SELECT placa FROM veiculos")["placa"].tolist()
    lc = db.get_dataframe("SELECT nome FROM condutores")["nome"].tolist()

    def rl(text,r,c):
        ctk.CTkLabel(form,text=text,font=ctk.CTkFont("Arial",10,"bold"),
                     text_color=C_MUTED).grid(row=r,column=c,padx=10,pady=(10,2),sticky="w")

    def re_(r,c,val="",w=220):
        e = ctk.CTkEntry(form,width=w,height=36)
        if val: e.insert(0,str(val))
        e.grid(row=r,column=c,padx=10,pady=(0,4)); return e

    try:
        data_display = datetime.strptime(str(reg["data"])[:10],"%Y-%m-%d").strftime("%d-%m-%Y")
    except Exception:
        data_display = str(reg.get("data",""))

    rl("Data (DD-MM-AAAA)",0,0); ent_data=re_(1,0,data_display)
    rl("Placa / Identificador",0,1)
    cb_placa = ctk.CTkComboBox(form,values=lv or [reg.get("placa","")],width=220,height=36)
    cb_placa.set(reg.get("placa","")); cb_placa.grid(row=1,column=1,padx=10,pady=(0,4))

    rl("Produto",2,0)
    cb_prod = ctk.CTkComboBox(form,
        values=["DIESEL S10","DIESEL S500","GASOLINA","ETANOL","ARLA 32","ÓLEO","FILTRO","PNEU","OUTRO"],
        width=220,height=36)
    cb_prod.set(reg.get("produto","")); cb_prod.grid(row=3,column=0,padx=10,pady=(0,4))

    rl("Condutor",2,1)
    cb_cond = ctk.CTkComboBox(form,values=lc or [reg.get("responsavel","")],width=220,height=36)
    cb_cond.set(reg.get("responsavel","")); cb_cond.grid(row=3,column=1,padx=10,pady=(0,4))

    # BUG FIX: substituído float(reg.get('campo', 0)) por _safe_float(reg.get('campo')).
    # dict.get(chave, default) só usa o default quando a chave NÃO existe no dict.
    # get_registro_by_id sempre inclui todas as colunas — com valor None para NULL.
    # Portanto reg.get('valor', 0) retorna None (não 0), e float(None) lança TypeError,
    # impedindo a abertura do diálogo para qualquer registro com campos nulos.
    rl("Valor R$",4,0)
    ent_val = re_(5,0, f"{_safe_float(reg.get('valor')):.2f}")
    rl("Quantidade (L)",4,1)
    ent_qtd = re_(5,1, f"{_safe_float(reg.get('quantidade')):.2f}")
    rl("Horímetro / KM",6,0)
    ent_hor = re_(7,0, f"{_safe_float(reg.get('horimetro')):.1f}")

    rl("Categoria",6,1)
    cb_cat = ctk.CTkComboBox(form,values=["ABASTECIMENTO","MANUTENÇÃO"],width=220,height=36)
    cb_cat.set(reg.get("categoria","ABASTECIMENTO")); cb_cat.grid(row=7,column=1,padx=10,pady=(0,4))

    def salvar():
        try:
            raw = ent_data.get().strip().replace("/","-")
            data_str = datetime.strptime(raw,"%d-%m-%Y").strftime("%Y-%m-%d")
            ok = db.update_registro(
                reg_id, data_str,
                cb_prod.get().upper(), cb_cond.get().upper(), cb_placa.get().upper(),
                float(ent_val.get().replace(",",".")),
                float(ent_qtd.get().replace(",",".")),
                float(ent_hor.get().replace(",",".")),
                cb_cat.get())
            if ok:
                messagebox.showinfo("Sucesso",f"Registro #{reg_id} atualizado!")
                win.destroy(); callback()
            else:
                messagebox.showerror("Erro","Não foi possível salvar.")
        except ValueError:
            messagebox.showerror("Erro","Data inválida ou campos numéricos incorretos.")

    bf = ctk.CTkFrame(win, fg_color="transparent")
    bf.pack(fill="x", padx=28, pady=20)
    ctk.CTkButton(bf, text="💾  Salvar alterações", fg_color=C_ACCENT, height=44,
                  font=ctk.CTkFont("Arial",13,"bold"),
                  command=salvar).pack(side="left",expand=True,fill="x",padx=(0,8))
    ctk.CTkButton(bf, text="Cancelar", fg_color=C_SURFACE,
                  border_width=1, border_color=C_BORDER, height=44,
                  command=win.destroy).pack(side="left",expand=True,fill="x")
    win.grab_set()
