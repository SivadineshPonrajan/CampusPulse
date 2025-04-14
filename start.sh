#!/bin/bash

source ~/.campuspulse/bin/activate

ask_continue() {
    echo "Do you want to continue the loop? (y/n)"
    read -t 30 -p "Press 'y' to continue within 30 seconds: " user_input
    if [[ "$user_input" != "y" ]]; then
        echo "Exiting script..."
        exit 0
    fi
}

while true; do
    ask_continue
    echo "===== Starting run at $(date) ====="
    timeout 2m python main.py
    echo "===== 12 hours passed, restarting script ====="
done
