import requests


from config.config import API_URL
from serial import getserial
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
    },headers={"device-serial":getserial()}, timeout=TIMEOUT)
    if(response.status_code==503):
        raise requests.exceptions.ConnectionError()
    return response

def startServiceCall(table, hangoutId, callNumber):
    url = BASE_URL + "/serviceCalls/start"
    
    response = requests.post(url,json={
        "table":table,
        "hangout":hangoutId,
        "callNumber":callNumber,
        "push":"true"
    },headers={"device-serial":getserial()},timeout=TIMEOUT)
    if(response.status_code==503):
        raise requests.exceptions.ConnectionError()
def endServiceCall(table, hangoutId, callNumber, responseTime,order):
    url = BASE_URL + "/serviceCalls/end"
    response = requests.post(url,json={
        "table":table,
        "hangout":hangoutId,
        "callNumber":callNumber,
        "responseTime":responseTime,
        "order":order,
        "push":"true"
    },headers={"device-serial":getserial()},timeout=TIMEOUT)

    if(response.status_code==503):
        raise requests.exceptions.ConnectionError()
def sendRatings(table, hangoutId, ratings):
    response = requests.post(BASE_URL + "/ratings", json={
        "table":table,
        "hangout": hangoutId,
        "ratings": ratings,
        "push":"true"
    },headers={"device-serial":getserial()}, timeout = TIMEOUT)
    if(response.status_code==503):
        raise requests.exceptions.ConnectionError()
    return response