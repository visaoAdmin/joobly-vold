from StorageQueue import StorageQueue,NonStorageQueue
from multiThread import Thread
import time
import requests
from background_api import endServiceCall,sendHangout,sendRatings,startServiceCall
from api import makeDeviceOnline

class SmileyRunner(object):
    def __init__(self):
        self.currentThread = Thread(lambda:())
        
        self.runnable = None
        self.timer = None
        self.currentThread.run = self.syncCalls
        
    def addSmiley(self,func,args):
        self.timer = time.time()
        self.runnable = (func,args)
        self.currentThread.start()


    def syncCalls(self):
        while(self.timer):
            if self.runnable:
                if((time.time() - self.timer)>20):
                    try:
                        self.runnable[0](*self.runnable[1])
                    except:
                        pass
                    self.timer = None
