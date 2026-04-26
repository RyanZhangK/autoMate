# PyInstaller spec for autoMate v1.0+
#
# Build (from project root):
#   pip install -e '.[mcp,browser]' pyinstaller
#   pyinstaller packaging/automate.spec --noconfirm
#
# Output: dist/automate/automate(.exe)  — a self-contained binary that ships
# the FastAPI server, the agent loop, all integrations, and the static SPA.
# The browser extension lives in extension/ and is not bundled (the user
# loads it into Chrome unpacked).

# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_submodules

# Resolve paths relative to this spec file so the build works from any CWD.
HERE = os.path.dirname(os.path.abspath(SPEC))
PROJECT_ROOT = os.path.dirname(HERE)

block_cipher = None

datas = [
    (os.path.join(PROJECT_ROOT, "automate/frontend/index.html"), "automate/frontend"),
    (os.path.join(PROJECT_ROOT, "automate/frontend/app.js"),     "automate/frontend"),
    (os.path.join(PROJECT_ROOT, "automate/frontend/styles.css"), "automate/frontend"),
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
    [os.path.join(HERE, "launcher.py")],
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["torch", "torchvision", "ultralytics", "supervision",
              "modelscope", "tensorflow", "matplotlib", "scipy", "pandas"],
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
