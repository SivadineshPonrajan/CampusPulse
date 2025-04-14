#!/bin/bash

sudo apt update && sudo apt install -y \
python3-dev python3-pip python3-setuptools \
libjpeg-dev zlib1g-dev libtiff5-dev libfreetype6-dev \
liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk \
build-essential chromium-chromedriver chromium \
wget unzip feh

echo "Setup completed. Proceed to setup Python Virtual Environment"