wget https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux-aarch64.tar.gz
tar -xvzf geckodriver-v0.36.0-linux-aarch64.tar.gz

chmod +x geckodriver
sudo mv geckodriver /usr/local/bin/

sudo apt install firefox-esr 
