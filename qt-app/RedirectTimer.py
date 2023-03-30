import time
from PyQt5.QtWidgets import QApplication, QDialog, QListWidgetItem
from multiThread import Thread
class RedirectTimer():
    def __init__(self):
        super(RedirectTimer,self).__init__()
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
    # def start(self):
    #     self.reset()
    def setRedirectTime(self,resetTime):
        self.resetTime = resetTime
        
    def run(self):
        while(self.timer):

            if self.runnable:
                try:
                    if((time.time() - self.timer)>self.resetTime):
                        try:
                            self.runnable[0](*self.runnable[1])
                            break
                            return
                        except:
                            pass
                        self.timer = None
                except:
                    pass
