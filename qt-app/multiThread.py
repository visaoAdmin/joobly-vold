from PyQt5.QtCore import QObject, QThread, pyqtSignal, QThreadPool, QRunnable
import time
import requests
import os
import pickle
# from api import sendHangout,startHangout,finishHangout,apiDict,startServiceCall,endServiceCall,sendRatings
thread_group=[]
globalPool = QThreadPool.globalInstance()
def initThreadGroup():
    for i in range(5):
        thread_group.append(QThread())


def longRunningFunction():
    for i in range(5):
            time.sleep(20)

def runInNewThread(self, taskFunction):
        try:
            self.thread = QThread()

            pool = QThreadPool.globalInstance()
            runnable = Runnable(taskFunction)
            pool.start(runnable)

            self.worker = Worker(taskFunction)
        except Exception as e:

            pass



class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, taskFunction):
        super(Worker, self).__init__()
        self.task = taskFunction

    def run(self):
        """Long-running task."""
        self.task()
        self.finished.emit()

class Runnable(QRunnable):
    # finished = pyqtSignal()
    # progress = pyqtSignal(int)

    def __init__(self, taskFunction):
        super().__init__()
        self.task = taskFunction

    def run(self):
        """Long-running task."""
        self.task()
        # self.finished.emit()
    
class Thread (QThread):
    def __init__(self,task):
        super().__init__()
        self.task=task
    def run(self):
        self.task()
class ReUsableThreadRunner(object):
    def __init__(self):
        self.name = None
        self.currentThread = Thread(lambda:())

        # self.functions = []
        self.currentThread.start()
    def launch(self,taskFunction):
        if(self.name == taskFunction.__name__):
            return
        self.name = taskFunction.__name__

        self.currentThread.run = taskFunction
        self.currentThread.start()
    #     self.functions.append(taskFunction)
   
    # def launcher(self):
    #     while(True):
            
    #         try:
    #             fn = self.functions.pop(0)
    #             fn()
    #         except Exception as e:
    #             pass



class StorageQueue():

    def __init__ (self,path):
        self.currentThread = Thread(lambda:())
        self.queue = []
        self.path = path
        try:
            with open(path,"rb") as f:
                self.queue = pickle.load(f)
        except:
            pass
        self.currentThread.run = self.syncer
        self.currentThread.start()

    def syncer(self):
        while(True):
            time.sleep(1)
            with open(self.path , "wb") as f:
                pickle.dump(self.queue,f)

    def push(self,functionName,arg):
        self.queue.append([functionName,arg])
    def peek(self):
        return self.queue[0]
    def pop(self):
        return self.queue.pop(0)
    def replaceFront(self,item):
        self.queue[0] = item
        


class MultiApiThreadRunner(object):
    def __init__(self,path):
        self.currentThread = Thread(lambda:())
        self.functions = []
        self.function_args = []
        self.currentThread.run = self.syncAPICalls
        self.hangouts = []
        self.currentThread.start()
        self.queue2 = StorageQueue("background_queue")
        # self.queue = StorageQueue(path)
    
    def addAPICall(self,func,args):

        self.queue2.push(func,args)
    def syncAPICalls(self):
        while(True):
            
            time.sleep(2)
            
            
            backgroundAPI = None
            try :
                backgroundAPI = self.queue2.peek()
            except Exception as e:

                pass
            if backgroundAPI:
                try:
                    

                    runFunction = backgroundAPI[0]
                    args = backgroundAPI[1]

                    
                    try:
                        r = runFunction(*args)
                        self.queue2.pop()
                        if(r.status_code==503):
                            continue
                    except  requests.exceptions.ConnectionError:
                        pass
                except:
                    
                    pass
            

