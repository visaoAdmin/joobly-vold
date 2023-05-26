import subprocess
API_URL="https://api.mywoobly.com"
APP_VERSION="1.4"
# API_URL="http://localhost:3000"
def getConnectedWifi():
    try:
        return subprocess.getoutput("iwgetid | grep -e 'SSID' | awk '{print $2}'").split("\"")[1]
    except:
        return "Not Connected"


