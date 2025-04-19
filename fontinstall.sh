#!/bin/bash

# Set Helvetica font URL
URL_HELVETICA="https://www.fontsarena.com/wp-content/uploads/2024/12/helvetica.zip"

# Create user font directory if it doesn't exist
FONT_DIR="$HOME/.fonts"
mkdir -p "$FONT_DIR"
cd "$FONT_DIR" || { echo "Failed to enter $FONT_DIR"; exit 1; }
echo "$(pwd)"
# Download the font archive
echo "Downloading Helvetica fonts..."
wget "$URL_HELVETICA" -O helvetica.zip || { echo "Download failed."; exit 1; }

# Extract the archive
echo "Extracting Helvetica fonts..."
mkdir -p helvetica
unzip -q helvetica.zip -d helvetica || { echo "Extraction failed."; exit 1; }

# Copy TTF files into the font directory
echo "Installing Helvetica fonts..."
cp helvetica/helvetica/Helvetica*.ttf ./ || { echo "Font files not found."; exit 1; }

# Clean up
rm -rf helvetica helvetica.zip
echo "Cleanup complete."

# Rebuild font cache
echo "Rebuilding font cache..."
fc-cache -f -v

echo "Helvetica fonts installed successfully."
