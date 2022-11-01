import requests

BASE_URL = "https://api.mywoobly.com"

def getConfig(serialNumber):
    print("getting config...")
    response = requests.get(BASE_URL + "/devices/"+serialNumber+"/config")
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
    })
    return response


def callWaiter(table, hangoutId, callNumber):
    response = requests.post(BASE_URL + "/pod-events", json={
        "table": table,
        "hangout": hangoutId,
        "callNumber": callNumber,
        "type": "WAITER_CALLED"
    })
    return response


def waiterArrived(table, hangoutId, callNumber, responseTime):
    response = requests.post(BASE_URL + "/pod-events", json={
        "table": table,
        "hangout": hangoutId,
        "callNumber": callNumber,
        "responseTime": responseTime,
        "type": "WAITER_ARRIVED"
    })
    return response


def serviceDelayed(table, hangoutId, callNumber):
    response = requests.post(BASE_URL + "/pod-events", json={
        "table": table,
        "hangout": hangoutId,
        "callNumber": callNumber,
        "type": "SERVICE_DELAYED"
    })
    return response

def rate(table, hangoutId, ratingType, rating):
    response = requests.post(BASE_URL + "/pod-events", json={
        "table": table,
        "hangout": hangoutId,
        "ratingType": ratingType,
        "rating": rating,
        "type": "RATING_SUBMITTED"
    })
    return response


def addMultipleRatings(table, hangoutId, ratings):
    response = requests.post(BASE_URL + "/pod-events", json={
        "table": table,
        "hangout": hangoutId,
        "type": "RATINGS_SUBMITTED",
        "ratings": ratings
    })
    return response

def notifyExperience(table, hangoutId, experience, previosExperience):
    response = requests.post(BASE_URL + "/pod-events", json={
        "table": table,
        "hangout": hangoutId,
        "experience": experience,
        "previousExperience": previosExperience,
        "type": "EXPERIENCE_CHANGED"
    })
    return response

def fetchTableId():
    response = requests.get(BASE_URL + "/pod/table")
    tableId = response.json().get("referenceId")
    print("TableId in fetchTableId", response.json())
    return tableId
