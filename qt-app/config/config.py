import subprocess
API_URL="https://api.woobly.squareboat.info"
APP_VERSION="1.1.1"
# API_URL="http://localhost:3000"
def getConnectedWifi():
    try:
        return subprocess.getoutput("iwgetid | grep -e 'SSID' | awk '{print $2}'").split("\"")[1]
    except:
        return "Not Connected"

def pullLatestCode():
    try:
        subprocess.getoutput("cd /home/pi/waiterlite-raspberry && git pull")
    except Exception as e:
        print(e)
