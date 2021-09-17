while fswatch -r -1 ~/Sites/raspberry-pi-playground/*; do
    rsync -aP ~/Sites/raspberry-pi-playground/ pi@192.168.1.29:~/scripts/
done
