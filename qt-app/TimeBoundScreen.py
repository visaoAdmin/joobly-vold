import time
from PyQt5.QtWidgets import QApplication, QDialog, QListWidgetItem
from multiThread import Thread
class TimeBoundScreen(QDialog):
    def __init__(self,time):
        super(TimeBoundScreen,self).__init__()
        self.resetTime = time
        self.thread = Thread(lambda:())
        self.timer = None
        self.runnable = None
        self.thread.run = self.run
    def setRunnable(self,functionName,functionArgsInArr):
        self.runnable = [functionName,functionArgsInArr]
    def reset(self):
        self.timer = time.time()
        self.thread.start()
    def stop(self):
        self.timer = None
    def start(self):
        self.reset()
    def run(self):
        while(self.timer):
            if self.runnable:
                try:
                    if((time.time() - self.timer)>self.resetTime):
                        try:
                            self.runnable[0](*self.runnable[1])
                            return
                        except:
                            pass
                        self.timer = None
                except:
                    pass
