# 📦 Como empacotar — Sistema Abastecimento ERP v11

---

## Pré-requisitos

```
Python 3.10 ou 3.11  (recomendado — evite 3.12+ com customtkinter)
Windows 10 / 11 x64
```

---

## 1 — Instalar dependências

```bat
pip install pyinstaller pandas matplotlib customtkinter openpyxl Pillow reportlab
```

Verifique se tudo instalou:

```bat
python -c "import customtkinter, pandas, matplotlib, openpyxl, PIL, reportlab; print('OK')"
```

---

## 2 — Estrutura de pastas esperada

```
projeto/
├── analisador.py          ← ponto de entrada
├── config.py
├── theme.py               ← NOVO (sistema de temas)
├── database.py
├── etl.py
├── export.py
├── logo.png
├── logo.ico               ← necessário para o ícone do .exe
├── SistemaAbastecimento.spec
└── ui/
    ├── __init__.py
    ├── app.py
    ├── widgets.py
    ├── dialogs.py
    └── views/
        ├── __init__.py
        ├── dashboard.py
        ├── frota.py
        ├── custos.py
        ├── registros.py
        ├── cadastros.py
        ├── importacao.py
        └── configuracoes.py
```

> **Atenção:** `theme.json` NÃO precisa existir antes de compilar.
> Ele é criado automaticamente quando o usuário troca o tema.

---

## 3 — Gerar o .exe

Sempre use o `.spec` (não o comando `--onefile` direto):

```bat
pyinstaller SistemaAbastecimento.spec --noconfirm --clean
```

- `--noconfirm` → sobrescreve a pasta `dist/` sem perguntar  
- `--clean`     → limpa o cache de builds anteriores (evita bugs de arquivos antigos)

O executável ficará em:

```
dist\SistemaAbastecimento.exe
```

---

## 4 — Testar antes de distribuir

```bat
cd dist
SistemaAbastecimento.exe
```

Se abrir sem erros, o build está bom. Se travar sem mensagem, rode temporariamente
com console para ver o erro:

No `.spec`, mude `console=False` para `console=True`, recompile, rode e leia o log.
Depois reverta para `console=False`.

---

## 5 — Montar a pasta de distribuição

O usuário final precisa de **uma pasta** com apenas estes arquivos:

```
SistemaAbastecimento_v11/
├── SistemaAbastecimento.exe    ← copiado de dist/
└── logo.png                   ← opcional (logo na sidebar)
```

O sistema cria automaticamente na mesma pasta:
- `abastecimento_erp_v11.db` → banco de dados
- `theme.json`               → preferência de tema

Não é necessário instalar Python na máquina do usuário.

---

## 6 — Rebuild rápido após editar um arquivo

```bat
pyinstaller SistemaAbastecimento.spec --noconfirm
```

Sem `--clean` é mais rápido (usa cache).
Use `--clean` apenas quando mudar dependências ou imports.

---

## Problemas comuns

| Sintoma | Causa | Solução |
|---|---|---|
| Antivírus bloqueia o .exe | Falso positivo do PyInstaller + UPX | Adicione exceção no antivírus ou remova `upx=True` do spec |
| "Módulo não encontrado" ao abrir | Import não detectado pelo PyInstaller | Adicione o módulo em `hiddenimports` no spec |
| Tela preta e fecha | Erro silencioso | Mude `console=False → True` temporariamente para ver o erro |
| "already exists" ao rodar 2x | Instância única funcionando | Normal — o sistema detecta a outra instância e avisa |
| theme.json ignorado | Arquivo fora da pasta do .exe | Coloque `theme.json` na **mesma pasta** que o `SistemaAbastecimento.exe` |
| Ícone não aparece | `logo.ico` não encontrado no build | Verifique se `logo.ico` existe na raiz do projeto antes de compilar |

---

## Dica: criar logo.ico a partir do logo.png

Se tiver apenas `logo.png`, gere o `.ico` com Python:

```python
from PIL import Image
img = Image.open("logo.png")
img.save("logo.ico", format="ICO",
         sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
print("logo.ico gerado!")
```

Execute uma vez antes de compilar:

```bat
python gerar_ico.py
```
