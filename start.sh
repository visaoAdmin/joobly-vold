#!/bin/bash

cd /home/pi/waiterlite-raspberry && 
sudo cp wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf &
sudo cp qt-app/assets/Splash.png /usr/share/plymouth/themes/pix/splash.png &
sudo cp desktop-items-0.conf /home/pi/.config/pcmanfm/LXDE-pi/desktop-items-0.conf &
sudo cp desktop-items-0.conf /etc/xdg/autostart/waiterLITE.desktop  &
git pull &
cd /home/pi/waiterlite-raspberry/qt-app && /usr/bin/python3 main.py