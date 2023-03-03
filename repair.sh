#!/bin/bash


while ! iwgetid | grep -e "SSID" ; do
        sleep 1
done

if cd /home/pi/waiterlite-raspberry && git pull | grep -e "fatal" 
then
        cd /home/pi && sudo rm -rf waiterlite-raspberry && git clone --branch develop https://aakash-woobly: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@github.com/Radien-Design/waiterlite-raspberry.git
else
        echo "Done 1"
fi

if grep -e "main.py" /home/pi/waiterlite-raspberry/start.sh
then
        echo "Done2"
else
        cd /home/pi && sudo rm -rf waiterlite-raspberry && git clone --branch develop https://aakash-woobly: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@github.com/Radien-Design/waiterlite-raspberry.git
fi