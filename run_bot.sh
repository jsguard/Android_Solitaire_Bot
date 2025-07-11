#!/bin/bash

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEST_DIR="$SCRIPT_DIR/platform-tools"
ANDROID_BRIDGE_FILE="$SCRIPT_DIR/android_bridge.dll"

# Copy the file if it exists
if [ -f "$ANDROID_BRIDGE_FILE" ]; then
    cp "$ANDROID_BRIDGE_FILE" "$DEST_DIR/"
    echo "Copied $(basename "$ANDROID_BRIDGE_FILE") to $DEST_DIR"
else
    echo "File not found: $ANDROID_BRIDGE_FILE"
fi

# Run the Python script
echo "Running main.py"
python "$SCRIPT_DIR/main.py"
