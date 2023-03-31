#!/bin/bash


cd /home/pi/waiterlite-raspberry && 
sudo cp qt-app/assets/Splash.png /usr/share/plymouth/themes/pix/splash.png &
sudo cp desktop-items-0.conf /home/pi/.config/pcmanfm/LXDE-pi/desktop-items-0.conf &
sudo cp waiterLITE.desktop /etc/xdg/autostart/waiterLITE.desktop  &
sudo cp waiterLITERepair.desktop /etc/xdg/autostart/waiterLITERepair.desktop  &
cd /home/pi/waiterlite-raspberry/qt-app && /usr/bin/python3 main.py &> /home/pi/lastLaunchLog.txt