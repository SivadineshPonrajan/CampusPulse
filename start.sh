#!/bin/bash

# SCRIPT_DIR="$(dirname "$(realpath "$0")")"
# LOG_FILE="$SCRIPT_DIR/campuspulse.log"

# echo "===== Started at $(date) =====" >> "$LOG_FILE"
echo "===== Started at $(date) ====="

# Try to connect for up to 10 seconds
SECONDS=0
while ! ping -c 1 -W 1 8.8.8.8 &> /dev/null; do
    if (( SECONDS >= 10 )); then
        echo "No internet after 10 seconds, continuing at $(date)"
        break
    fi
    sleep 1
done

echo "===== Started again at $(date) ====="

source ~/.campuspulse/bin/activate
cd /home/$(ls /home | head -n 1)/Desktop/campuspulse/
echo "===== Starting run at $(date) ====="
python /home/$(ls /home | head -n 1)/Desktop/campuspulse/main.py
