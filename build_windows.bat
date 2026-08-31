@echo off
REM Windows Build Script for Face Swap Avatar Virtual Webcam
REM This script builds the Python application into a standalone .exe

echo ========================================
echo Face Swap Avatar - Windows Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ and add it to your system PATH
    pause
    exit /b 1
)

REM Check if pip is available
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip is not available
    pause
    exit /b 1
)

echo [1/5] Installing build dependencies...
pip install pyinstaller --upgrade
if %errorlevel% neq 0 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

echo [2/5] Installing application dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)

echo [3/5] Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "__pycache__" rmdir /s /q __pycache__

echo [4/5] Building .exe with PyInstaller...

REM Ask user which version to build
set /p BUILD_TYPE="Build GUI version [G] or Command-line version [C]? (default: G): "
if "%BUILD_TYPE%"=="" set BUILD_TYPE=G

if /i "%BUILD_TYPE%"=="G" (
    echo Building GUI version...
    pyinstaller face_swap_avatar_gui.spec
) else (
    echo Building Command-line version...
    pyinstaller face_swap_avatar.spec
)

if %errorlevel% neq 0 (
    echo ERROR: PyInstaller build failed
    pause
    exit /b 1
)

echo [5/5] Build complete!
echo.
echo ========================================
echo Build Successful!
echo ========================================
echo.
echo Your executable is located at:
echo   dist\FaceSwapAvatar\FaceSwapAvatar.exe
echo.
echo Before running:
echo   1. Create an "avatars" folder in the same directory as the .exe
echo   2. Add 7 avatar images (center.jpg, left_30.jpg, left_45.jpg, etc.)
echo   3. Download inswapper_128.onnx model and place it next to the .exe
echo.
echo To run:
echo   dist\FaceSwapAvatar\FaceSwapAvatar.exe [--config config.json] [--camera 0] [--no-preview]
echo.
pause
