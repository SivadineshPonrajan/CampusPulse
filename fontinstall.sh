#!/bin/bash

# Set ARIAL font URL
URL_ARIAL="https://fontsarena.com/wp-content/uploads/2024/12/arial.zip" 

# Create user font directory if it doesn't exist
FONT_DIR="$HOME/.fonts"
mkdir -p "$FONT_DIR"
cd "$FONT_DIR" || { echo "Failed to enter $FONT_DIR"; exit 1; }
echo "$(pwd)"
# Download the font archive
echo "Downloading ARIAL fonts..."
wget "$URL_ARIAL" -O arial.zip || { echo "Download failed."; exit 1; }

# Extract the archive
echo "Extracting ARIAL fonts..."
mkdir -p arial
unzip -q arial.zip -d arial || { echo "Extraction failed."; exit 1; }

# Copy TTF files into the font directory
echo "Installing ARIAL fonts..."
cp arial/arial/ARIAL*.TTF ./ || { echo "Font files not found."; exit 1; }

# Clean up
rm -rf arial arial.zip
echo "Cleanup complete."

# Rebuild font cache
echo "Rebuilding font cache..."
fc-cache -f -v

echo "Helvetica fonts installed successfully."
