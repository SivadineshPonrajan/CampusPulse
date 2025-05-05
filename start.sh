#!/bin/bash

source ~/.campuspulse/bin/activate
echo "===== Starting run at $(date) ====="
python /home/$(ls /home | head -n 1)/Desktop/campuspulse/main.py