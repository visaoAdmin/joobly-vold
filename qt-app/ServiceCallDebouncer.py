from StorageQueue import StorageQueue,NonStorageQueue
from multiThread import Thread
import time
import requests
from background_api import endServiceCall,sendHangout,sendRatings,startServiceCall
from api import makeDeviceOnline

class ServiceCallDebouncer(object):
    def __init__(self):
        self.currentThread = Thread(lambda:())
        
        self.runnable = None
        self.timer = None
        self.currentThread.run = self.syncCalls
        
    def call(self,func,args):
        self.timer = time.time()
        self.runnable = (func,args)
        self.currentThread.start()

    def stop(self):
        if self.timer != None:
            self.timer = None
            return True
        return False

    def syncCalls(self):
        while(self.timer):
            if self.runnable and self.timer:
                executeRunnable = False
                try:
                    executeRunnable = (time.time() - self.timer)>3
                except:
                    pass
                if(executeRunnable):
                    try:
                        self.runnable[0](*self.runnable[1])
                    except:
                        pass
                    self.timer = None
