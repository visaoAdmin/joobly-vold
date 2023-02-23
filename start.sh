#!/bin/bash

cd /home/pi/waiterlite-raspberry && 
sudo cp wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf &
git pull &
cd /home/pi/waiterlite-raspberry/qt-app && /usr/bin/python3 main.py