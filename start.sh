#!/bin/bash

cd /home/pi/waiterlite-raspberry && 
sudo cp wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf &
sudo cp qt-app/assets/Splash.png /usr/share/plymouth/themes/pix/splash.png &
git pull &
cd /home/pi/waiterlite-raspberry/qt-app && /usr/bin/python3 main.py