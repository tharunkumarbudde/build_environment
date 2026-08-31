# Build & Deployment Guide 🔨

Complete guide for building the Face Swap Avatar as a standalone .exe application.

## Table of Contents
1. [Windows Build](#windows-build)
2. [Linux/Mac Build](#linuxmac-build)
3. [Packaging for Distribution](#packaging-for-distribution)
4. [Installer Creation](#installer-creation)
5. [Troubleshooting](#troubleshooting)

## Windows Build

### Prerequisites
- Python 3.10 or higher (add to PATH during installation)
- pip package manager
- ~2 GB free disk space for build

### Step 1: Prepare Source

```bash
cd /path/to/build_environment
```

### Step 2: Install Build Tools

```bash
# Install PyInstaller and dependencies
pip install pyinstaller
pip install -r requirements.txt
```

### Step 3: Automated Build

**Easiest method:**

```bash
build_windows.bat
```

This will:
1. Install PyInstaller
2. Install all dependencies from requirements.txt
3. Clean previous builds
4. Build the .exe using PyInstaller
5. Create a ready-to-use distribution

**Output location:** `dist/FaceSwapAvatar/`

### Step 4: Manual Build (Alternative)

If the batch script doesn't work:

```bash
# Clean previous builds
rmdir /s /q build
rmdir /s /q dist

# Build with PyInstaller
pyinstaller face_swap_avatar.spec
```

### Customizing the Build

Edit `face_swap_avatar.spec` to customize:

```python
# Change exe name
name='MyCustomName',

# Add icon
icon='path/to/icon.ico',

# Customize console
console=True,  # False for GUI-only (no console)

# Add custom data
datas=[
    ('avatars', 'avatars'),
    ('models', 'models'),
]
```

## Linux/Mac Build

### Prerequisites
- Python 3.10+
- pip
- Build tools (`build-essential` on Linux)

### Step 1: Install Dependencies

```bash
# Linux
sudo apt-get install python3-dev build-essential

# Mac
brew install python3
```

### Step 2: Prepare Project

```bash
cd /path/to/build_environment
chmod +x build.sh
```

### Step 3: Build

```bash
./build.sh
```

**Output location:** `dist/FaceSwapAvatar/`

### Running on Linux

After build, the executable is in `dist/FaceSwapAvatar/FaceSwapAvatar`

```bash
# Make executable
chmod +x dist/FaceSwapAvatar/FaceSwapAvatar

# Run
./dist/FaceSwapAvatar/FaceSwapAvatar --help
```

## Packaging for Distribution

### Step 1: Prepare Distribution Folder

```
MyApp/
├── FaceSwapAvatar.exe (or binary)
├── avatars/
│   ├── center.jpg
│   ├── left_30.jpg
│   ├── left_45.jpg
│   ├── right_30.jpg
│   ├── right_45.jpg
│   ├── up_20.jpg
│   └── down_20.jpg
├── inswapper_128.onnx
├── config_default.json
└── README.txt
```

### Step 2: Create README.txt for Users

```text
FACE SWAP AVATAR VIRTUAL WEBCAM
================================

QUICK START:
1. Make sure you have a virtual camera installed
   - Windows: Install OBS Studio with VirtualCam plugin
   - Mac: Install CamTwist
   - Linux: sudo modprobe v4l2loopback

2. Run FaceSwapAvatar.exe

3. In Zoom/Teams/Google Meet:
   - Settings → Video/Camera
   - Select "FaceSwapAvatar" or virtual camera

SETTINGS:
- Edit config_default.json to customize
- Run with --help for command line options

HELP:
- Check SETUP_GUIDE.md for troubleshooting
- Verify avatars folder has all 7 images
- Ensure inswapper_128.onnx is present

REQUIREMENTS:
- NVIDIA GPU recommended (but works on CPU)
- 8GB RAM minimum
- Webcam required
```

### Step 3: Create Launch Script

**Windows: run.bat**
```batch
@echo off
cd /d "%~dp0"
FaceSwapAvatar.exe %*
pause
```

**Windows: run_no_console.bat**
```batch
@echo off
cd /d "%~dp0"
start "" FaceSwapAvatar.exe %*
```

**Mac/Linux: run.sh**
```bash
#!/bin/bash
cd "$(dirname "$0")"
./FaceSwapAvatar --no-preview "$@"
```

### Step 4: Create Shortcut (Windows)

Create a shortcut to `run.bat`:
1. Right-click → New → Shortcut
2. Target: `run.bat`
3. Start in: `(current folder)`
4. Add icon if desired

## Installer Creation

### Option 1: NSIS Installer (Windows)

Install NSIS: http://nsis.sourceforge.net/

Create `installer.nsi`:

```nsis
; FaceSwapAvatar Installer

!include "MUI2.nsh"

; Basic settings
Name "Face Swap Avatar"
OutFile "FaceSwapAvatar_Setup.exe"
InstallDir "$PROGRAMFILES\FaceSwapAvatar"

; Pages
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES

; Language
!insertmacro MUI_LANGUAGE "English"

; Installer sections
Section "Install"
  SetOutPath "$INSTDIR"
  File /r "dist\FaceSwapAvatar\*.*"
  File "avatars\*.*"
  File "inswapper_128.onnx"
  File "config_default.json"
  File "run.bat"
  
  ; Create Start Menu shortcuts
  CreateDirectory "$SMPROGRAMS\FaceSwapAvatar"
  CreateShortcut "$SMPROGRAMS\FaceSwapAvatar\FaceSwapAvatar.lnk" "$INSTDIR\run.bat"
  CreateShortcut "$SMPROGRAMS\FaceSwapAvatar\Uninstall.lnk" "$INSTDIR\uninstall.exe"
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

; Uninstaller
Section "Uninstall"
  Delete "$INSTDIR\*.*"
  RMDir /r "$INSTDIR"
  RMDir /r "$SMPROGRAMS\FaceSwapAvatar"
SectionEnd
```

Build installer:
```bash
makensis installer.nsi
```

### Option 2: WinRAR SFX Archive

1. Select all files in distribution folder
2. Add to archive (WinRAR)
3. Tools → Create self-extracting archive
4. Set extraction path to `$PROGRAMFILES\FaceSwapAvatar`

### Option 3: Inno Setup

Download: http://www.jrsoftware.org/isdl.php

More user-friendly than NSIS for simple installers.

## Build Optimization

### Reduce Executable Size

Edit `face_swap_avatar.spec`:

```python
# Strip binaries
strip=True,

# Exclude unused modules
excludedimports=['matplotlib', 'pandas', 'tensorflow'],

# Use UPX compression
upx=True,
```

### Faster Builds

```bash
# Skip validation
pyinstaller --noconfirm face_swap_avatar.spec

# Parallel build
pyinstaller -j 4 face_swap_avatar.spec
```

### Code Signing (Optional)

On Windows with code signing certificate:

```bash
signtool sign /f certificate.pfx /p password /t timestamp_server dist\FaceSwapAvatar\FaceSwapAvatar.exe
```

## Continuous Integration / Automated Builds

### GitHub Actions Example

Create `.github/workflows/build.yml`:

```yaml
name: Build Face Swap Avatar

on: [push, pull_request]

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install pyinstaller -r requirements.txt
      - run: pyinstaller face_swap_avatar.spec
      - uses: actions/upload-artifact@v2
        with:
          name: FaceSwapAvatar-Windows
          path: dist/FaceSwapAvatar/

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install pyinstaller -r requirements.txt
      - run: pyinstaller face_swap_avatar.spec
      - uses: actions/upload-artifact@v2
        with:
          name: FaceSwapAvatar-Linux
          path: dist/FaceSwapAvatar/

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install pyinstaller -r requirements.txt
      - run: pyinstaller face_swap_avatar.spec
      - uses: actions/upload-artifact@v2
        with:
          name: FaceSwapAvatar-Mac
          path: dist/FaceSwapAvatar/
```

## Distribution Checklist

- [ ] Build created without errors
- [ ] All avatar images included
- [ ] Model file (inswapper_128.onnx) present
- [ ] Config file included
- [ ] README/documentation included
- [ ] Run script works
- [ ] Tested on clean machine (no Python installed)
- [ ] File size reasonable (100-500MB depending on dependencies)
- [ ] Version number updated
- [ ] Installer (if creating one) tested

## Troubleshooting

### "PyInstaller: command not found"
```bash
pip install pyinstaller
```

### "ModuleNotFoundError" after building
Add missing module to `hiddenimports` in `.spec` file:
```python
hiddenimports=['module_name'],
```

### .exe won't run on other machines
- Ensure Microsoft Visual C++ Redistributables installed
- Check Python version (3.10+ recommended)
- Verify all dependencies packaged correctly

### Large executable file (1+ GB)
This is normal with heavy dependencies (OpenCV, ONNX, etc.). To reduce:
- Remove unused libraries from `hiddenimports`
- Use UPX compression
- Distribute as installer instead of loose binary

### Virtual camera not found in .exe
- Ensure virtual camera installed before running .exe
- Paths may differ from source code version
- Test source Python version first

## Advanced: Custom Python Executable

For maximum compatibility, create custom Python environment:

```bash
# Create clean virtual environment
python -m venv venv_build
venv_build\Scripts\activate

# Install minimal dependencies
pip install -r requirements.txt
pip install pyinstaller

# Build
pyinstaller face_swap_avatar.spec

# Deactivate
deactivate
```

## Version Management

Update version in multiple places:

**In spec file:**
```python
name='FaceSwapAvatar_v1.2.0',
```

**In source code:**
```python
__version__ = "1.2.0"
```

**In config:**
```json
{"version": "1.2.0"}
```

---

**Happy building! 🚀**

For more info, see:
- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/)
- [SETUP_GUIDE.md](SETUP_GUIDE.md)
- [README.md](README.md)
