#!/bin/bash
cd /home/pi/waiterlite-raspberry && 
git pull origin &
./startup-scripts.sh &
cd /home/pi/waiterlite-raspberry/qt-app && export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES && 
rq worker high --with-scheduler & /usr/bin/python3 main.py
