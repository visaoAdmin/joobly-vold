from StorageQueue import StorageQueue
from multiThread import Thread
import time
import requests
from background_api import endServiceCall,sendHangout,sendRatings,startServiceCall
class QueueWorker(object):
    def __init__(self):
        self.currentThread = Thread(lambda:())
        self.functions = []
        self.function_args = []
        
        self.hangouts = []
        self.queue = StorageQueue("function_queue.file")
        self.queue2 = StorageQueue("background_queue.file")
        self.currentThread.run = self.syncAPICalls

        self.currentThread.start()

    
    def addAPICall(self,func,args):
        # print(func,args)
        self.queue.push(func,args)

    def syncAPICalls(self):
        while(True):
            
            # time.sleep(2)
            while(len(self.queue.queue)>0):
                print("Queue ",self.queue.queue)
                foregroundAPI = None
                try :
                    
                    foregroundAPI = self.queue.peek()
                except Exception as e:
                    # print(e)
                    pass
                if foregroundAPI:
                    try:
                        
                        
                        # print("2nd",runFunction)
                        
                        try:
                            print("2--",foregroundAPI)
                            runFunction = foregroundAPI[0]
                            args = foregroundAPI[1]
                            r = runFunction(*args)
                            self.queue.pop()
                            print(r)
                            if(r.status_code==503):
                                raise  Exception()
                        except Exception as e: 
                            print(e)
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
                    except:
                        pass
                        
                        
            

            
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
                    print("Background API",backgroundAPI)        
                    runFunction = backgroundAPI[0]
                    args = backgroundAPI[1]
                    r = runFunction(*args)
                    self.queue2.pop()
                    # print("3--",backgroundAPI)
                    # print(len(self.queue2.queue))
                    # print("peeking")
                    # print(self.queue2.peek())
                    # print("peek end")
                    # print(r)
                    
                    if(r==None or r.status_code==503):
                        raise requests.exceptions.ConnectionError()
                except  requests.exceptions.ConnectionError:
                    pass
                except Exception as e:
                    # print(e)
                    self.queue2.pop()
                
                    

