import requests
from config.config import API_URL
import os
import copy
from background_api import sendHangout,startServiceCall,endServiceCall,sendRatings
from redis_queue import backgroundQueue
from rq import Retry, Queue
from redis_handler import failure_handler
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
    
    print("startHangout",table, guestCount, waiterId, hangoutId)
    response = requests.post(BASE_URL + "/pod-events", json={
        "table": table,
        "guestCount": guestCount,
        "waiter": waiterId,
        "hangout": hangoutId,
        "type": "CHECKIN"
    }, timeout=TIMEOUT)
    return response
    

def startHangoutFailureHandler(job, connection, type, value, traceback):
    global background_jobs,index
    
    args = job.__dict__['_args']
    # print("$$$$$$$$$$$$$$$$$$$$$",args)
    table,guestCount,waiterId,hangoutId = args 
    if(index==-1):
        job1 =  backgroundQueue.enqueue(sendHangout,table, guestCount, waiterId, hangoutId ,on_failure=failure_handler)
    else:
        job1 = backgroundQueue.enqueue(sendHangout,table, guestCount, waiterId, hangoutId, on_failure=failure_handler)
        print(job1.__dict__['_func_name']," depends on ",background_jobs(index).__dict__['_func_name'])
    background_jobs.append(job1)
    index+=1

def finishHangout(hangoutId):
    # print("startHangout",hangoutId)
    response = requests.patch(BASE_URL + "/hangouts/"+hangoutId,json={
        "status":"COMPLETED"
    })
    return response


def callWaiter(table, hangoutId, callNumber):

    print("CAlling waiter")
    response = requests.post(BASE_URL + "/pod-events", json={
        "table": table,
        "hangout": hangoutId,
        "callNumber": callNumber,
        "type": "WAITER_CALLED"
    }, timeout = TIMEOUT)
    return response
def callWaiterFailureHandler(job, connection, type, value, traceback):    
    global background_jobs,index
    # print(background_jobs)
    args = job.__dict__['_args']
    table,hangoutId,callNumber=args
    if(index==-1):
        job1 = backgroundQueue.enqueue(startServiceCall,table, hangoutId, callNumber,on_failure=failure_handler )
    else:
        job1 = backgroundQueue.enqueue(startServiceCall,table, hangoutId, callNumber, on_failure=failure_handler )
    background_jobs.append(job1)
    index+=1

def waiterArrived(table, hangoutId, callNumber, responseTime):
    
    print("waiter arrived")
    response = requests.post(BASE_URL + "/pod-events", json={
        "table": table,
        "hangout": hangoutId,
        "callNumber": callNumber,
        "responseTime": responseTime,
        "type": "WAITER_ARRIVED"
    }, timeout = TIMEOUT)
    return response
    

def waiterArrivedFailureHandler(job, connection, type, value, traceback):
    global background_jobs,index
    args = job.__dict__['_args']
    table ,hangoutId,callNumber,responseTime=args
    if(index==-1):
        job1 =  backgroundQueue.enqueue(endServiceCall,table, hangoutId, callNumber, responseTime ,on_failure=failure_handler)
    else:
        job1 = backgroundQueue.enqueue(endServiceCall,table, hangoutId, callNumber, responseTime, on_failure=failure_handler )
    background_jobs.append(job1)
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
    
    print("rating sent")
    response = requests.post(BASE_URL + "/pod-events", json={
        "table": table,
        "hangout": hangoutId,
        "type": "RATINGS_SUBMITTED",
        "ratings": ratings
    }, timeout = TIMEOUT)
    return response
    
    
def addMultipleRatingsFailureHandler(job, connection, type, value, traceback):
    global background_jobs,index
    args = job.__dict__['_args']
    table ,hangoutId,ratings=args
    # if(index==-1):
    job1 = backgroundQueue.enqueue(sendRatings,table, hangoutId, ratings ,on_failure=failure_handler)
    # else:
    #     job1 = backgroundQueue.enqueue(sendRatings,table, hangoutId, ratings,depends_on = background_jobs[index] )
    # background_jobs.append(job1)
    # index+=1
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