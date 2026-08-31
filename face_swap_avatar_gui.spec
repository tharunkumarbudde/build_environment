# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for building Face Swap Avatar GUI as a clean onedir bundle.
Run: pyinstaller face_swap_avatar_gui.spec
"""

from PyInstaller.utils.hooks import collect_submodules

insightface_imports = collect_submodules('insightface')
pyvc_imports = collect_submodules('pyvirtualcam')

hidden_imports = (
    ['numpy', 'onnxruntime', 'psutil', 'cv2', 'PyQt5']
    + insightface_imports
    + pyvc_imports
)

all_datas = [
    ('avatars', 'avatars'),
    ('settings.json', '.'),
]

a = Analysis(
    ['face_swap_avatar_gui.py'],
    pathex=[],
    binaries=[],
    datas=all_datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name='FaceSwapAvatar',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FaceSwapAvatar',
)
