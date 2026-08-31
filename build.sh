#!/bin/bash

# Linux/Mac Build Script for Face Swap Avatar Virtual Webcam

echo "========================================"
echo "Face Swap Avatar - Build Script"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

echo "Python version: $(python3 --version)"
echo ""

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 is not available"
    exit 1
fi

# Install PyInstaller
echo "[1/5] Installing build dependencies..."
pip3 install pyinstaller --upgrade
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install PyInstaller"
    exit 1
fi

# Install dependencies
echo "[2/5] Installing application dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install requirements"
    exit 1
fi

# Clean previous builds
echo "[3/5] Cleaning previous builds..."
rm -rf build dist __pycache__

# Build with PyInstaller
echo "[4/5] Building with PyInstaller..."

# Ask user which version to build
read -p "Build GUI version [G] or Command-line version [C]? (default: G): " BUILD_TYPE
BUILD_TYPE=${BUILD_TYPE:-G}

if [[ "$BUILD_TYPE" == "G" || "$BUILD_TYPE" == "g" ]]; then
    echo "Building GUI version..."
    pyinstaller face_swap_avatar_gui.spec
else
    echo "Building Command-line version..."
    pyinstaller face_swap_avatar.spec
fi

if [ $? -ne 0 ]; then
    echo "ERROR: PyInstaller build failed"
    exit 1
fi

echo "[5/5] Build complete!"
echo ""
echo "========================================"
echo "Build Successful!"
echo "========================================"
echo ""
echo "Your executable is located at:"
echo "  dist/FaceSwapAvatar/FaceSwapAvatar"
echo ""
echo "Before running:"
echo "  1. Create an 'avatars' folder in the same directory as the executable"
echo "  2. Add 7 avatar images (center.jpg, left_30.jpg, left_45.jpg, etc.)"
echo "  3. Download inswapper_128.onnx model and place it next to the executable"
echo ""
echo "To run:"
echo "  ./dist/FaceSwapAvatar/FaceSwapAvatar [--config config.json] [--camera 0] [--no-preview]"
echo ""
