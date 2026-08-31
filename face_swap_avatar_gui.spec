# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for building Face Swap Avatar GUI as Windows .exe
Run: pyinstaller face_swap_avatar_gui.spec
"""

a = Analysis(
    ['face_swap_avatar_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include avatar images if they exist
        ('avatars', 'avatars'),
        ('settings.json', '.'),
    ],
    hiddenimports=[
        'insightface',
        'insightface.app',
        'insightface.model_zoo',
        'onnxruntime',
        'cv2',
        'numpy',
        'pyvirtualcam',
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'psutil',
    ],
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
