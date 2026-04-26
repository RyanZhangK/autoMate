# PyInstaller spec for autoMate v1.0+
#
# Build:
#   pip install -e '.[full]' pyinstaller
#   pyinstaller packaging/automate.spec --noconfirm
#
# Output: dist/automate/automate(.exe)  — a self-contained binary that ships
# the FastAPI server, the agent loop, all integrations, and the static SPA.
# The browser extension lives in extension/ and is not bundled (the user
# loads it into Chrome unpacked).

# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

datas = [
    ("../automate/frontend/index.html", "automate/frontend"),
    ("../automate/frontend/app.js",     "automate/frontend"),
    ("../automate/frontend/styles.css", "automate/frontend"),
]

hiddenimports = []
hiddenimports += collect_submodules("automate")
hiddenimports += collect_submodules("uvicorn")
hiddenimports += [
    "uvicorn.logging",
    "uvicorn.loops.auto",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan.on",
]

a = Analysis(
    ["../automate/__main__.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["torch", "torchvision", "ultralytics", "supervision", "modelscope", "tensorflow"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="automate",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="automate",
)
