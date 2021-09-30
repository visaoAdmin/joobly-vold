while fswatch -r -1 ~/Sites/raspberry-pi-playground/*; do
    rsync -aP ~/Sites/raspberry-pi-playground/ pi@raspberrypi.local:~/scripts/
done
