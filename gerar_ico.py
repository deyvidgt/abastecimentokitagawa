# gerar_ico.py — converte logo.png para logo.ico
# Execute UMA VEZ antes de rodar o PyInstaller
# Requer: pip install Pillow

from PIL import Image
import os

src = "logo.png"
dst = "logo.ico"

if not os.path.exists(src):
    print(f"Arquivo '{src}' não encontrado na pasta atual.")
    raise SystemExit(1)

img = Image.open(src).convert("RGBA")
img.save(
    dst,
    format="ICO",
    sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)],
)
print(f"✅  '{dst}' gerado com sucesso a partir de '{src}'")
