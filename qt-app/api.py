import requests

BASE_URL = "https://api.mywoobly.com"

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
    response = requests.get(BASE_URL + "/restaurants/"+restaurantId+"/tables", timeout = TIMEOUT)
    tables = response.json()
    return tables.get("data").get("tables")
