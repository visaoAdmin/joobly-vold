python3 main.py &
PID=$!
export ENV=dev
while fswatch -r -1 ~/Sites/raspberry-pi-playground/*; do
    # exit the existing process
    echo $PID
    echo "Changed, restarting..."j
    kill -9 $PID
    python3 main.py &
    PID=$!
done