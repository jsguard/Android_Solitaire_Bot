#!/bin/bash

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEST_DIR="$SCRIPT_DIR/platform-tools"

# Detect OS
case "$(uname -s)" in
    Linux*)     OS_TYPE="linux";;
    Darwin*)    OS_TYPE="mac";;
    MINGW*|MSYS*|CYGWIN*) OS_TYPE="windows";;
    *)          echo "❌ Unsupported OS: $(uname -s)"; exit 1;;
esac

# Set download URL based on OS
case "$OS_TYPE" in
    linux)   SDK_URL="https://dl.google.com/android/repository/platform-tools-latest-linux.zip";;
    mac)     SDK_URL="https://dl.google.com/android/repository/platform-tools-latest-darwin.zip";;
    windows) SDK_URL="https://dl.google.com/android/repository/platform-tools-latest-windows.zip";;
esac

echo "Detected OS: $OS_TYPE"

# Skip download if platform-tools already exists
if [ -d "$DEST_DIR" ]; then
    echo "Platform Tools already installed in: $DEST_DIR"
else
    echo "Downloading from: $SDK_URL"

    # Change to script directory
    cd "$SCRIPT_DIR"

    # Download
    curl -L -o platform-tools.zip "$SDK_URL"

    # Remove any existing folder before extracting
    rm -rf "$DEST_DIR"

    # Extract
    echo "Extracting..."
    unzip -q platform-tools.zip -d "$SCRIPT_DIR"
    rm platform-tools.zip

    echo "Platform Tools installed in: $DEST_DIR"
fi

echo ""
echo "To use adb or fastboot, add this to your PATH:"
echo "export PATH=\"\$PATH:$DEST_DIR\""

echo "Installing dependencies"
pip install -r requirements.txt