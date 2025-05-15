#!/bin/bash

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
LOG_FILE="$SCRIPT_DIR/campuspulse.log"

echo "===== Started at $(date) =====" >> "$LOG_FILE"

source ~/.campuspulse/bin/activate
echo "===== Starting run at $(date) ====="
python /home/$(ls /home | head -n 1)/Desktop/campuspulse/main.py
