from StorageQueue import StorageQueue,NonStorageQueue
from multiThread import Thread
import time
import datetime
import requests
from background_api import endServiceCall,sendHangout,sendRatings,startServiceCall
from api import makeDeviceOnline
class QueueWorker(object):
    def __init__(self):
        self.currentThread = Thread(lambda:())
        self.functions = []
        self.function_args = []
        
        self.hangouts = []
        self.queue = NonStorageQueue()
        self.queue2 = StorageQueue("background_queue.file")
        self.currentThread.run = self.syncAPICalls

        self.currentThread.start()

    
    def addAPICall(self,func,args):
        # print(func,args)
        self.queue.push(func,args)

    def syncAPICalls(self):
        prev = 1
        prev+=1
        while(True):
            
            # time.sleep(2)
            while(len(self.queue.queue)>0):
                # print("Queue ",self.queue.queue)
                foregroundAPI = None
                try :
                    
                    foregroundAPI = self.queue.peek()
                except Exception as e:

                    with open("logFile.txt","a+") as logFile:
                        logFile.write("\n"+str(datetime.datetime.now())+" "+runFunction.__name__+" "+str(args)+"\n"+str(e)+"\n")
                if foregroundAPI:
                    try:
                        
                        
                        # print("2nd",runFunction)
                        
                        try:

                            runFunction = foregroundAPI[0]
                            args = foregroundAPI[1]
                            r = runFunction(*args)
                            self.queue.pop()

                                    

                            if(r ==None or r.status_code!=200):
                                raise  Exception()
                        except Exception as e: 
                            with open("logFile.txt","a+") as logFile:
                                logFile.write("\n"+str(datetime.datetime.now())+" "+runFunction.__name__+" "+str(args)+"\n"+str(e)+"\n")


                            if(runFunction.__name__=="startHangout"):
                                self.queue2.push(sendHangout,[*args])
                            elif(runFunction.__name__=="callWaiter"):
                                self.queue2.push(startServiceCall,[*args])
                            elif(runFunction.__name__=="waiterArrived"):
                                self.queue2.push(endServiceCall,[*args])
                            elif(runFunction.__name__=="addMultipleRatings"):
                                self.queue2.push(sendRatings,[*args])
                            self.queue.pop()
                            pass
                    except Exception as e:
                        with open("logFile.txt","a+") as logFile:
                            logFile.write("\n"+str(datetime.datetime.now())+" "+runFunction.__name__+" "+str(args)+"\n"+str(e)+"\n")
                        
                        
            

            
            # while(len(self.queue2.queue)>0):
                # print(self.queue2.queue)
            # time.sleep(1)
            backgroundAPI = None
            try :
                backgroundAPI = self.queue2.peek()

            except Exception as e:
                # print(e)
                pass
            if backgroundAPI:
                    # print("2nd",runFunction)
                    
                try:
                    # print("Background API",backgroundAPI)        
                    runFunction = backgroundAPI[0]
                    prev = backgroundAPI
                    args = backgroundAPI[1]
                    r = runFunction(*args)
                    self.queue2.pop()
                    if(r==None or r.status_code!=503):
                        # self.queue2.push(runFunction,args)
                        raise requests.exceptions.ConnectionError()
                    
                    
                    
                    
                except  requests.exceptions.ConnectionError:
                    pass
                except Exception as e:
                    print(3)
                    with open("logFile.txt","a+") as logFile:
                        logFile.write("\n"+str(datetime.datetime.now())+" "+runFunction.__name__+" "+str(args)+"\n"+str(e)+"\n")
                    pass
            else:
                try:
                    if(prev[0].__name__!="sendRatings"):
                        makeDeviceOnline(prev[1][1])
                    prev = 1
                except:
                    pass
                    

