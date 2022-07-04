#!/bin/bash
cd /home/pi/waiterlite-raspberry && 
git pull origin &
./startup-scripts.sh &
cd qt-app && /usr/bin/python3 main.py
