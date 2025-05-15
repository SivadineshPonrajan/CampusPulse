#!/bin/bash

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
LOG_FILE="$SCRIPT_DIR/campuspulse.log"

echo "===== Started at $(date) =====" >> "$LOG_FILE"

# Try to connect for up to 5 seconds
SECONDS=0
while ! ping -c 1 -W 1 8.8.8.8 &> /dev/null; do
    if (( SECONDS >= 5 )); then
        echo "No internet after 5 seconds, continuing at $(date)" >> "$LOG_FILE"
        break
    fi
    sleep 1
done

echo "===== Started again at $(date) =====" >> "$LOG_FILE"

source ~/.campuspulse/bin/activate
echo "===== Starting run at $(date) ====="
python /home/$(ls /home | head -n 1)/Desktop/campuspulse/main.py
