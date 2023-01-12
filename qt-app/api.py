import requests
from config.config import API_URL
import os



BASE_URL = API_URL
print("BASE_URL",BASE_URL)
TIMEOUT = 15

def getConfig(serialNumber):
    print("getting config...")
    response = requests.get(BASE_URL + "/devices/"+serialNumber+"/config", timeout = TIMEOUT)
    print(response)
    config = response.json().get("data")
    return config


def startHangout(table, guestCount, waiterId, hangoutId):
    print("startHangout",table, guestCount, waiterId, hangoutId)
    response = requests.post(BASE_URL + "/pod-events", json={
        "table": table,
        "guestCount": guestCount,
        "waiter": waiterId,
        "hangout": hangoutId,
        "type": "CHECKIN"
    }, timeout=TIMEOUT)
    return response

def finishHangout(hangoutId):
    # print("startHangout",hangoutId)
    response = requests.patch(BASE_URL + "/hangouts/"+hangoutId,json={
        "status":"COMPLETED"
    })
    return response


def callWaiter(table, hangoutId, callNumber):
    response = requests.post(BASE_URL + "/pod-events", json={
        "table": table,
        "hangout": hangoutId,
        "callNumber": callNumber,
        "type": "WAITER_CALLED"
    }, timeout = TIMEOUT)
    return response


def waiterArrived(table, hangoutId, callNumber, responseTime):
    response = requests.post(BASE_URL + "/pod-events", json={
        "table": table,
        "hangout": hangoutId,
        "callNumber": callNumber,
        "responseTime": responseTime,
        "type": "WAITER_ARRIVED"
    }, timeout = TIMEOUT)
    return response


def serviceDelayed(table, hangoutId, callNumber):
    response = requests.post(BASE_URL + "/pod-events", json={
        "table": table,
        "hangout": hangoutId,
        "callNumber": callNumber,
        "type": "SERVICE_DELAYED"
    }, timeout = TIMEOUT)
    return response

def rate(table, hangoutId, ratingType, rating):
    response = requests.post(BASE_URL + "/pod-events", json={
        "table": table,
        "hangout": hangoutId,
        "ratingType": ratingType,
        "rating": rating,
        "type": "RATING_SUBMITTED"
    }, timeout = TIMEOUT)
    return response

def waiterExists(waiterId,restaurantId):
    response = requests.get(BASE_URL + "/waiters/"+str(waiterId)+"/restaurants/"+str(restaurantId)+"/exists",timeout=TIMEOUT)
    # print(response.json())
    return response.json()['data']['waiterExists']

def addMultipleRatings(table, hangoutId, ratings):
    response = requests.post(BASE_URL + "/pod-events", json={
        "table": table,
        "hangout": hangoutId,
        "type": "RATINGS_SUBMITTED",
        "ratings": ratings
    }, timeout = TIMEOUT)
    return response

def notifyExperience(table, hangoutId, experience, previosExperience):
    response = requests.post(BASE_URL + "/pod-events", json={
        "table": table,
        "hangout": hangoutId,
        "experience": experience,
        "previousExperience": previosExperience,
        "type": "EXPERIENCE_CHANGED"
    }, timeout = TIMEOUT)
    return response

def fetchTableId():
    response = requests.get(BASE_URL + "/pod/table", timeout = TIMEOUT)
    tableId = response.json().get("referenceId")
    print("TableId in fetchTableId", response.json())
    return tableId

def getAllTables(restaurantId):
    url = BASE_URL + "/restaurants/"+restaurantId+"/tables"
    response = requests.get(url, timeout = TIMEOUT)
    
    tables = response.json()
    return tables.get("data").get("tables")

# def syncHangOut(hangoutId,hangout):
#     url = BASE_URL + "/hangouts/"+hangoutId+"/sync"
#     response = requests.post(url,json=hangout)

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
def callWaiter(table, hangoutId, callNumber):
    response = requests.post(BASE_URL + "/pod-events", json={
        "table": table,
        "hangout": hangoutId,
        "callNumber": callNumber,
        "type": "WAITER_CALLED"
    }, timeout = TIMEOUT)
    return response


def waiterArrived(table, hangoutId, callNumber, responseTime):
    response = requests.post(BASE_URL + "/pod-events", json={
        "table": table,
        "hangout": hangoutId,
        "callNumber": callNumber,
        "responseTime": responseTime,
        "type": "WAITER_ARRIVED"
    }, timeout = TIMEOUT)
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
apiDict ={
    "getConfig":getConfig,
    "startHangout":startHangout,
    "waiterArrived":waiterArrived,
    "callWaiter":callWaiter,
    "finishHangout":finishHangout,
    "addMultipleRatings":addMultipleRatings
    
}