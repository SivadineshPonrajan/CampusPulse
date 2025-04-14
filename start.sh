#!/bin/bash

ask_continue() {
    echo "Do you want to continue the loop? (y/n)"
    read -t 30 -p "Press 'y' to continue within 30 seconds: " user_input
    if [[ "$user_input" == "n" ]]; then
        echo "Exiting script..."
        exit 0
    fi
}

while true; do
    ask_continue
    echo "===== Starting run at $(date) ====="
    timeout 2m ~/.campuspulse/bin/python main.py
    echo "===== 12 hours passed, restarting script ====="
done
