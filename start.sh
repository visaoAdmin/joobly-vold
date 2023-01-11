#!/bin/bash
cd /home/pi/waiterlite-raspberry && 
git restore . &&
git pull origin &
./startup-scripts.sh &
cd /home/pi/waiterlite-raspberry/qt-app && /usr/bin/python3 main.py
