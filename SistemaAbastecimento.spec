# -*- mode: python ; coding: utf-8 -*-
# SistemaAbastecimento.spec — PyInstaller onefile, sem console
# Fix v2: collect_all para numpy e matplotlib (resolve _philox e outros .pyd Cython)

import os
import customtkinter
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None
CTK_PATH = os.path.dirname(customtkinter.__file__)

# =================================================================
# collect_all garante que os binários Cython (.pyd/.so) sejam
# incluídos — hiddenimports sozinho NÃO copia os arquivos físicos.
# =================================================================
numpy_datas,      numpy_bins,      numpy_hidden      = collect_all('numpy')
matplotlib_datas, matplotlib_bins, matplotlib_hidden = collect_all('matplotlib')
pandas_datas,     pandas_bins,     pandas_hidden     = collect_all('pandas')

a = Analysis(
    ['analisador.py'],
    pathex=['.'],
    binaries=[
        *numpy_bins,
        *matplotlib_bins,
        *pandas_bins,
    ],
    datas=[
        ('logo.png', '.'),
        ('logo.ico', '.'),
        (CTK_PATH,  'customtkinter'),
        *numpy_datas,
        *matplotlib_datas,
        *pandas_datas,
    ],
    hiddenimports=[
        # ── UI ────────────────────────────────────────────────────
        'customtkinter',
        'PIL._tkinter_finder',
        'PIL.Image',
        'PIL.ImageTk',
        # ── Numpy (collect_all + lista explícita de segurança) ────
        *numpy_hidden,
        'numpy.random._bounded_integers',
        'numpy.random._common',
        'numpy.random._generator',
        'numpy.random._mt19937',
        'numpy.random._pcg64',
        'numpy.random._philox',
        'numpy.random._sfc64',
        'numpy.random.bit_generator',
        'numpy.random.mtrand',
        'numpy.core._dtype_ctypes',
        'numpy.core._multiarray_tests',
        # ── Matplotlib ────────────────────────────────────────────
        *matplotlib_hidden,
        'matplotlib.backends.backend_tkagg',
        'matplotlib.backends.backend_agg',
        # ── Pandas ────────────────────────────────────────────────
        *pandas_hidden,
        'pandas.io.formats.style',
        # ── Excel / PDF ───────────────────────────────────────────
        'openpyxl',
        'openpyxl.cell._writer',
        'reportlab',
        'reportlab.platypus',
        'reportlab.graphics',
        # ── Módulos internos do projeto ───────────────────────────
        'theme',
        'config',
        'database',
        'etl',
        'export',
        'ui',
        'ui.app',
        'ui.widgets',
        'ui.dialogs',
        'ui.views',
        'ui.views.dashboard',
        'ui.views.frota',
        'ui.views.custos',
        'ui.views.registros',
        'ui.views.cadastros',
        'ui.views.importacao',
        'ui.views.configuracoes',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pytest', 'IPython', 'jupyter', 'PyQt5', 'PyQt6', 'wx'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SistemaAbastecimento',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # mude para True se precisar ver erros
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='logo.ico',
)
