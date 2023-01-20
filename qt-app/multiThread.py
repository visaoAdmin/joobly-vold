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
            # Step 3: Create a worker object
            pool = QThreadPool.globalInstance()
            runnable = Runnable(taskFunction)
            pool.start(runnable)

            self.worker = Worker(taskFunction)
        except Exception as e:
            print(e)
            pass
        # Step 4: Move worker to the thread
        
        # self.worker.moveToThread(self.thread)
        
        # Step 5: Connect signals and slots
        
        # self.thread.started.connect(self.worker.run)
        # self.worker.finished.connect(self.thread.quit)
        # self.worker.finished.connect(self.worker.deleteLater)
        # self.thread.finished.connect(self.thread.deleteLater)
        
        # worker.progress.connect(reportProgress)
        # Step 6: Start the thread
        
        # self.thread.start()


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
        self.currentThread = Thread(lambda:())
        self.currentThread.run = self.launcher
        self.functions = []
        self.currentThread.start()
    def launch(self,taskFunction):
        self.functions.append(taskFunction)
   
    def launcher(self):
        while(True):
            try:
                self.functions.pop(0)()
            except:
                pass
            # while( len(self.functions)!=0):
                # self.funct`ions[0]()

        # self.worker = Worker(taskFunction)

class ServiceCallsSyncer(object):
    def __init__(self):
        self.currentThread = Thread(lambda:())
        print("Creatad New Thread")
        self.queue = []
        
    def addServiceCall(self,hangOut):
        print("Added New Thread")
        self.queue.append(hangOut)
        # print(self.queue)
        self.currentThread.run = self.syncServiceCalls
        self.currentThread.start()
    
    def syncServiceCalls(self):
        print("Syncing ")
        print(self.queue)
        while((len(self.queue)!=0)):
            hangOut = self.queue.pop(0)
            
            tableId = hangOut['tableId']
            del hangOut['tableId']
            waiterId = hangOut['waiterId']
            del hangOut['waiterId']
            guestCount = hangOut['guestCount']
            del hangOut['guestCount']
            hangoutId = hangOut['hangoutId']
            hangOut[len(hangOut)-1]['total'] = time.time() - hangOut[len(hangOut)-1]['open']
            print(hangOut)
            while(True):
                try:
                    startHangout(tableId,guestCount,waiterId,hangoutId)
                    break
                except requests.exceptions.ConnectionError:
                    print("Connection error")
                    time.sleep(0.1)
                except Exception as e:
                    break
            while(True):
                try:
                    syncHangOut(hangoutId,hangOut)
                    break
                except requests.exceptions.ConnectionError:
                    print("Connection error")
                    time.sleep(0.1)
                except Exception as e:
                    break
            while(True):
                try:
                    finishHangout(hangoutId)
                    break
                except requests.exceptions.ConnectionError:
                    print("Connection error")
                    time.sleep(0.1)
                
                except Exception as e:
                    break


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
        print("Queueu",self.queue)
        print(self.queue)
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
        print("CAlled")
        print(func,args)
        self.queue2.push(func,args)
    def syncAPICalls(self):
        while(True):
            
            time.sleep(2)
            
            
            backgroundAPI = None
            try :
                backgroundAPI = self.queue2.peek()
            except Exception as e:
                print(e)
                pass
            if backgroundAPI:
                try:
                    
                    print("2--",backgroundAPI)
                    runFunction = backgroundAPI[0]
                    args = backgroundAPI[1]
                    # print("2nd",runFunction)
                    
                    try:
                        r = runFunction(*args)
                        self.queue2.pop()
                        if(r.status_code==503):
                            continue
                    except  requests.exceptions.ConnectionError:
                        pass
                except:
                    
                    pass
            

