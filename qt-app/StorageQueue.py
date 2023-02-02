from multiThread import Thread
import pickle
import time
class StorageQueue():

    def __init__ (self,path):
        # self.currentThread = Thread(lambda:())
        self.queue = []
        self.path = path
        try:
            with open(path,"rb") as f:
                self.queue = pickle.load(f)
        except:
            pass
        # print("Queueu",self.queue)
        # print(self.queue)
        # self.currentThread.run = self.syncer
        # self.currentThread.start()

    def push(self,functionName,arg):
        self.queue.append([functionName,arg])
        with open(self.path , "wb") as f:
                pickle.dump(self.queue,f)
                print("added")
    
    def peek(self):
        if(len(self.queue)>0):
            return self.queue[0]
        return []

    
    def pop(self):
        if(len(self.queue)<=0):
            return []
        res =  self.queue.pop(0)
        with open(self.path , "wb") as f:
                pickle.dump(self.queue,f)
        return res
    
    def replaceFront(self,item):
        self.queue[0] = item

class NonStorageQueue():

    def __init__ (self):
        # self.currentThread = Thread(lambda:())
        self.queue = []
        
        # print("Queueu",self.queue)
        # print(self.queue)
        # self.currentThread.run = self.syncer
        # self.currentThread.start()

    def push(self,functionName,arg):
        self.queue.append([functionName,arg])
        
    
    def peek(self):
        if(len(self.queue)>0):
            return self.queue[0]
        return []

    
    def pop(self):
        if(len(self.queue)<=0):
            return []
        res =  self.queue.pop(0)
        
        return res
    
    def replaceFront(self,item):
        self.queue[0] = item