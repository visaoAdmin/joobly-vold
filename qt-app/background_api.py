import requests


from config.config import API_URL
BASE_URL = API_URL
TIMEOUT = 15

def sendHangout(table, guestCount, waiterId, hangoutId):
    url = BASE_URL + "/hangouts"
    response = requests.post(url, json={
        "table": table,
        "guestCount": guestCount,
        "waiter": waiterId,
        "hangout": hangoutId,
        "push":"true"
    }, timeout=TIMEOUT)
    return response

def startServiceCall(table, hangoutId, callNumber):
    url = BASE_URL + "/serviceCalls/start"
    
    response = requests.post(url,json={
        "table":table,
        "hangout":hangoutId,
        "callNumber":callNumber,
        "push":"true"
    },timeout=TIMEOUT)
def endServiceCall(table, hangoutId, callNumber, responseTime):
    url = BASE_URL + "/serviceCalls/end"
    response = requests.post(url,json={
        "table":table,
        "hangout":hangoutId,
        "callNumber":callNumber,
        "responseTime":responseTime,
        "push":"true"
    },timeout=TIMEOUT)
def sendRatings(table, hangoutId, ratings):
    response = requests.post(BASE_URL + "/ratings", json={
        "hangout": hangoutId,
        "ratings": ratings,
        "push":"true"
    }, timeout = TIMEOUT)
    return response