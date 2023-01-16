import requests
from config.config import API_URL
import os
import copy
from background_api import sendHangout,startServiceCall,endServiceCall,sendRatings
from redis_queue import backgroundQueue,handle_failure
from rq import Retry, Queue

background_jobs = []
index = -1

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
    try:
        print("startHangout",table, guestCount, waiterId, hangoutId)
        response = requests.post(BASE_URL + "/pod-events", json={
            "table": table,
            "guestCount": guestCount,
            "waiter": waiterId,
            "hangout": hangoutId,
            "type": "CHECKIN"
        }, timeout=TIMEOUT)
        return response
    except:
        global background_jobs,index
        if(index==-1):
            job =  backgroundQueue.enqueue(sendHangout,table, guestCount, waiterId, hangoutId,retry=Retry(max=8640, interval=10),on_failure=handle_failure)
        else:
            job = backgroundQueue.enqueue(sendHangout,table, guestCount, waiterId, hangoutId,depends_on = background_jobs[index],retry=Retry(max=8640, interval=10))
        background_jobs.append(job)
        index+=1

def finishHangout(hangoutId):
    # print("startHangout",hangoutId)
    response = requests.patch(BASE_URL + "/hangouts/"+hangoutId,json={
        "status":"COMPLETED"
    })
    return response


def callWaiter(table, hangoutId, callNumber):
    try:
        print("CAlling waiter")
        response = requests.post(BASE_URL + "/pod-events", json={
            "table": table,
            "hangout": hangoutId,
            "callNumber": callNumber,
            "type": "WAITER_CALLED"
        }, timeout = TIMEOUT)
        return response
    except:
        global background_jobs,index
        if(index==-1):
            job = backgroundQueue.enqueue(startServiceCall,table, hangoutId, callNumber,retry=Retry(max=8640, interval=10))
        else:
            job = backgroundQueue.enqueue(startServiceCall,table, hangoutId, callNumber,depends_on = background_jobs[index],retry=Retry(max=8640, interval=10))
        background_jobs.append(job)
        index+=1
def waiterArrived(table, hangoutId, callNumber, responseTime):
    try:
        print("waiter arrived")
        response = requests.post(BASE_URL + "/pod-events", json={
            "table": table,
            "hangout": hangoutId,
            "callNumber": callNumber,
            "responseTime": responseTime,
            "type": "WAITER_ARRIVED"
        }, timeout = TIMEOUT)
        return response
    except:
        global background_jobs,index
        if(index==-1):
            job =  backgroundQueue.enqueue(endServiceCall,table, hangoutId, callNumber, responseTime,retry=Retry(max=8640, interval=10))
        else:
            job = backgroundQueue.enqueue(endServiceCall,table, hangoutId, callNumber, responseTime,depends_on = background_jobs[index],retry=Retry(max=8640, interval=10))
        background_jobs.append(job)
        index+=1
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
    try:
        print("rating sent")
        response = requests.post(BASE_URL + "/pod-events", json={
            "table": table,
            "hangout": hangoutId,
            "type": "RATINGS_SUBMITTED",
            "ratings": ratings
        }, timeout = TIMEOUT)
        return response
    except:
        global background_jobs,index
        if(index==-1):
            job = backgroundQueue.enqueue(sendRatings,table, hangoutId, ratings,retry=Retry(max=8640, interval=10))
        else:
            job = backgroundQueue.enqueue(sendRatings,table, hangoutId, ratings,depends_on = background_jobs[index],retry=Retry(max=8640, interval=10))
        background_jobs.append(job)
        index+=1
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

apiDict ={
    "getConfig":getConfig,
    "startHangout":startHangout,
    "waiterArrived":waiterArrived,
    "callWaiter":callWaiter,
    "finishHangout":finishHangout,
    "addMultipleRatings":addMultipleRatings
    
}