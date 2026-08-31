# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for building Face Swap Avatar GUI as Windows .exe
Run: pyinstaller face_swap_avatar_gui.spec
"""

from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_dynamic_libs

cv2_imports = collect_submodules('cv2')
insightface_imports = collect_submodules('insightface')
pyvc_imports = collect_submodules('pyvirtualcam')
qt_imports = collect_submodules('PyQt5')

hidden_imports = (
    ['numpy', 'onnxruntime', 'psutil', 'cv2']
    + cv2_imports
    + insightface_imports
    + pyvc_imports
    + qt_imports
)

all_datas = [('avatars', 'avatars'), ('settings.json', '.')]
all_datas += collect_data_files('cv2')
all_datas += collect_data_files('PyQt5')

all_binaries = []
all_binaries += collect_dynamic_libs('cv2')
all_binaries += collect_dynamic_libs('onnxruntime')


a = Analysis(
    ['face_swap_avatar_gui.py'],
    pathex=[],
    binaries=all_binaries,
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FaceSwapAvatar',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI application - no console
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Set to icon file path for custom icon
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
