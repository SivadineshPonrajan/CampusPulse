#!/bin/bash

# Set ARIAL font URL
URL_ARIAL="https://fontsarena.com/wp-content/uploads/2024/12/arial.zip" 

DOWN_DIR="/home/$(ls /home | head -n 1)/Desktop"
cd "$DOWN_DIR"
echo "$(pwd)"
echo "Downloading ARIAL fonts..."
wget "$URL_ARIAL" -O arial.zip || { echo "Download failed."; exit 1; }
echo "$(pwd)"
echo "Extracting ARIAL fonts..."
mkdir -p arial
unzip -q arial.zip -d arial || { echo "Extraction failed."; exit 1; }

FONT_DIR="/home/$(ls /home | head -n 1)/.fonts"
mkdir -p "$FONT_DIR"

echo "Installing ARIAL fonts..."
cp arial/arial/ARIAL*.TTF $FONT_DIR || { echo "Font files not found."; exit 1; }

# Clean up
rm -rf arial arial.zip
echo "Cleanup complete."

# Rebuild font cache
echo "Rebuilding font cache..."
fc-cache -f -v

echo "Fonts installed successfully."