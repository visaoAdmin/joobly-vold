from PyQt5.QtCore import QObject, QThread, pyqtSignal, QThreadPool, QRunnable
import time
import requests
from api import syncHangOut,startHangout,finishHangout
thread_group=[]
globalPool = QThreadPool.globalInstance()
def initThreadGroup():
    for i in range(5):
        thread_group.append(QThread())


def longRunningFunction():
    for i in range(5):
            time.sleep(20)

def runInNewThread(self, taskFunction):
        self.thread = QThread()
        # Step 3: Create a worker object
        pool = QThreadPool.globalInstance()
        runnable = Runnable(taskFunction)
        pool.start(runnable)

        self.worker = Worker(taskFunction)
        
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
        
    def recycle(self):
        self
        self.currentThread.exit()
    def launch(self,taskFunction):
        self.recycle()
        self.run = taskFunction
        self.currentThread.start()
        self.worker = Worker(taskFunction)

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
                    time.sleep(1)
                except Exception as e:
                    break
            while(True):
                try:
                    syncHangOut(hangoutId,hangOut)
                    break
                except requests.exceptions.ConnectionError:
                    print("Connection error")
                    time.sleep(1)
                except Exception as e:
                    break
            while(True):
                try:
                    finishHangout(hangoutId)
                    break
                except requests.exceptions.ConnectionError:
                    print("Connection error")
                    time.sleep(1)
                
                except Exception as e:
                    break

            


