import requests
from config.config import API_URL
import os
import copy
from background_api import sendHangout,startServiceCall,endServiceCall,sendRatings
from serial import getserial
# from redis_queue import backgroundQueue
# from rq import Retry, Queue
# from redis_handler import failure_handler
from multiThread import MultiApiThreadRunner

backgroundRunner = MultiApiThreadRunner("function_queue")

restartApp = False

def setRestartAppFalse():
    global restartApp
    restartApp = False

def setRestartApp(res):
    global restartApp
    if(res.status_code==401):
        restartApp = True
    else:
        restartApp = False
def getRestartApp():
    global restartApp
    return restartApp

background_jobs = []
index = -1

BASE_URL = API_URL
# print("BASE_URL",BASE_URL)
TIMEOUT = 15

def getConfig(serialNumber):
    # print("getting config...")
    response = requests.get(BASE_URL + "/devices/"+serialNumber+"/config", timeout = TIMEOUT)
    # print(response)
    setRestartApp(response)
    config = response.json().get("data")
    return config


def startHangout(table, guestCount, waiterId, hangoutId):
    setRestartAppFalse()
    # print("startHangout",table, guestCount, waiterId, hangoutId)
    response = requests.post(BASE_URL + "/pod-events", json={
        "table": table,
        "guestCount": guestCount,
        "waiter": waiterId,
        "hangout": hangoutId,
        "type": "CHECKIN"
    },headers={"device-serial":getserial()}, timeout=TIMEOUT)
    if(response.status_code==503):
        raise Exception()
    
    return response
    

def startHangoutFailureHandler(job, connection, type, value, traceback):
    global background_jobs,index
    
    args = job.__dict__['_args']
    # print("$$$$$$$$$$$$$$$$$$$$$",args)
    table,guestCount,waiterId,hangoutId = args
    backgroundRunner.addAPICall(sendHangout,[table,guestCount,waiterId,hangoutId]) 
    # if(index==-1):
    #     job1 =  backgroundQueue.enqueue(sendHangout,table, guestCount, waiterId, hangoutId ,on_failure=failure_handler)
    # else:
    #     job1 = backgroundQueue.enqueue(sendHangout,table, guestCount, waiterId, hangoutId, on_failure=failure_handler)
    #     print(job1.__dict__['_func_name']," depends on ",background_jobs(index).__dict__['_func_name'])
    # background_jobs.append(job1)
    # index+=1

def finishHangout(hangoutId):
    # print("startHangout",hangoutId)
    response = requests.patch(BASE_URL + "/hangouts/"+hangoutId,json={
        "status":"COMPLETED"
    })
    return response


def callWaiter(table, hangoutId, callNumber):

    # print("CAlling waiter")
    response = requests.post(BASE_URL + "/pod-events", json={
        "table": table,
        "hangout": hangoutId,
        "callNumber": callNumber,
        "type": "WAITER_CALLED"
    },headers={"device-serial":getserial()}, timeout = TIMEOUT)
    if(response.status_code==503):
        raise Exception()
    setRestartApp(response)
    return response
def callWaiterFailureHandler(job, connection, type, value, traceback):    
    global background_jobs,index
    # print(background_jobs)
    args = job.__dict__['_args']
    table,hangoutId,callNumber=args
    backgroundRunner.addAPICall(startServiceCall,[table,hangoutId,callNumber])
    # if(index==-1):
    #     job1 = backgroundQueue.enqueue(startServiceCall,table, hangoutId, callNumber,on_failure=failure_handler )
    # else:
    #     job1 = backgroundQueue.enqueue(startServiceCall,table, hangoutId, callNumber, on_failure=failure_handler )
    # background_jobs.append(job1)
    # index+=1

def waiterArrived(table, hangoutId, callNumber, responseTime):
    
    print("waiter arrived")
    response = requests.post(BASE_URL + "/pod-events", json={
        "table": table,
        "hangout": hangoutId,
        "callNumber": callNumber,
        "responseTime": responseTime,
        "type": "WAITER_ARRIVED"
    },headers={"device-serial":getserial()}, timeout = TIMEOUT)
    if(response.status_code==503):
        raise Exception()
    setRestartApp(response)
    return response
    

def waiterArrivedFailureHandler(job, connection, type, value, traceback):
    global background_jobs,index
    args = job.__dict__['_args']
    table ,hangoutId,callNumber,responseTime=args
    backgroundRunner.addAPICall(endServiceCall,[table,hangoutId,callNumber,responseTime])
    # if(index==-1):
    #     job1 =  backgroundQueue.enqueue(endServiceCall,table, hangoutId, callNumber, responseTime ,on_failure=failure_handler)
    # else:
    #     job1 = backgroundQueue.enqueue(endServiceCall,table, hangoutId, callNumber, responseTime, on_failure=failure_handler )
    # background_jobs.append(job1)
    # index+=1

def serviceDelayed(table, hangoutId, callNumber):
    response = requests.post(BASE_URL + "/pod-events", json={
        "table": table,
        "hangout": hangoutId,
        "callNumber": callNumber,
        "type": "SERVICE_DELAYED"
    },headers={"device-serial":getserial()}, timeout = TIMEOUT)
    return response

def rate(table, hangoutId, ratingType, rating):
    response = requests.post(BASE_URL + "/pod-events", json={
        "table": table,
        "hangout": hangoutId,
        "ratingType": ratingType,
        "rating": rating,
        "type": "RATING_SUBMITTED"
    },headers={"device-serial":getserial()}, timeout = TIMEOUT)
    return response

def waiterExists(waiterId,restaurantId):
    response = requests.get(BASE_URL + "/waiters/"+str(waiterId)+"/restaurants/"+str(restaurantId)+"/exists",timeout=TIMEOUT)
    # print(response.json())
    if(response.status_code==503):
        raise Exception()
    return response.json()['data']['waiterExists']

def addMultipleRatings(table, hangoutId, ratings):
    
    # print("rating sent")
    global restartApp
    response = requests.post(BASE_URL + "/pod-events", json={
        "table": table,
        "hangout": hangoutId,
        "type": "RATINGS_SUBMITTED",
        "ratings": ratings
    },headers={"device-serial":getserial()}, timeout = TIMEOUT)
    if(response.status_code==503):
        raise Exception()
    setRestartApp(response)
    return response
    
    
def addMultipleRatingsFailureHandler(job, connection, type, value, traceback):
    global background_jobs,index
    args = job.__dict__['_args']
    table ,hangoutId,ratings=args
    # if(index==-1):
    backgroundRunner.addAPICall(sendRatings,[table,hangoutId,ratings])
    # job1 = backgroundQueue.enqueue(sendRatings,table, hangoutId, ratings ,on_failure=failure_handler)
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
    },headers={"device-serial":getserial()}, timeout = TIMEOUT)
    return response

def fetchTableId():
    response = requests.get(BASE_URL + "/pod/table", timeout = TIMEOUT)
    tableId = response.json().get("referenceId")
    # print("TableId in fetchTableId", response.json())
    return tableId

def getAllTables(restaurantId):
    url = BASE_URL + "/restaurants/"+restaurantId+"/tables"
    response = requests.get(url,headers={"device-serial":getserial()}, timeout = TIMEOUT)
    
    tables = response.json()
    return tables.get("data").get("tables")

def isTableOccupied(table):
    url = BASE_URL + "/tables/"+ table +"/hangout/open"
    response = requests.get(url,headers={"device-serial":getserial()}, timeout=TIMEOUT)
    return response

def changeDevice(hangout):
    url = BASE_URL + "/hangouts/"+ hangout +"/device/"+getserial()
    response = requests.post(url,timeout=TIMEOUT)
    setRestartApp(response)
# def syncHangOut(hangoutId,hangout):
#     url = BASE_URL + "/hangouts/"+hangoutId+"/sync"
#     response = requests.post(url,json=hangout)

def makeDeviceOnline(hangoutId):
    url = BASE_URL + "/hangouts/" + hangoutId +"/online"
    response = requests.get(url,timeout=TIMEOUT)

def notifyFeelingBad(hangout,waiter,restaurant,table):
    response = requests.post(BASE_URL + "/pod-events", json={
        "table": table,
        "hangout": hangout,
        "waiter":waiter,
        "restaurant":restaurant,
        "type": "CUSTOMER_SAD",
    })
def notifyFeelingNeutral(hangout,waiter,restaurant,table):
    response = requests.post(BASE_URL + "/pod-events", json={
        "table": table,
        "hangout": hangout,
        "waiter":waiter,
        "restaurant":restaurant,
        "type": "CUSTOMER_NEUTRAL",
    })
def notifyFeelingHappy(hangout,waiter,restaurant,table):
    response = requests.post(BASE_URL + "/pod-events", json={
        "table": table,
        "hangout": hangout,
        "waiter":waiter,
        "restaurant":restaurant,
        "type": "CUSTOMER_HAPPY",
    })

apiDict ={
    "getConfig":getConfig,
    "startHangout":startHangout,
    "waiterArrived":waiterArrived,
    "callWaiter":callWaiter,
    "finishHangout":finishHangout,
    "addMultipleRatings":addMultipleRatings
    
}