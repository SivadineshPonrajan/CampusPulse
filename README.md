# CampusPulse
CampusPulse - University community connected with everyday announcements, events, and updates - all in one dynamic display.

sudo apt-get remove realvnc-vnc-server

'
python -m venv ~/.campuspulse

source ~/.campuspulse/bin/activate

python -m pip install --upgrade pip

pip install -r requirements.txt --no-input

'




[Desktop Entry]
Type=Application
Name=CampusPulse
Exec=/home/$(ls /home | head -n 1)/Desktop/campuspulse/start.sh
X-GNOME-Autostart-enabled=true

