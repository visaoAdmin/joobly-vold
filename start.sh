#!/bin/bash

sudo chmod -R 755 /home/pi/waiterlite-raspberry &
cd /home/pi/waiterlite-raspberry && 
sudo cp wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf &
sudo cp qt-app/assets/Splash.png /usr/share/plymouth/themes/pix/splash.png &
sudo cp desktop-items-0.conf /home/pi/.config/pcmanfm/LXDE-pi/desktop-items-0.conf &
sudo cp waiterLITE.desktop /etc/xdg/autostart/waiterLITE.desktop  &
sudo cp waiterLITERepair.desktop /etc/xdg/autostart/waiterLITERepair.desktop  &
cp repair.sh /home/pi/repair.sh &
cd /home/pi/waiterlite-raspberry/qt-app && /usr/bin/python3 main.py