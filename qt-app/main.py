import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPixmap, QImage,QIcon
from PyQt5.QtWidgets import QApplication, QDialog, QListWidgetItem
from PyQt5.QtCore import QSize,pyqtSignal,pyqtSlot
from TimeBoundScreen import TimeBoundScreen
import os 
from SmileyRunner import SmileyRunner
import copy 
from datetime import datetime
import signal
import urllib.request
from api import startHangout, callWaiter, waiterArrived, notifyExperience, addMultipleRatings, getConfig, waiterExists
from api import isTableOccupied, changeDevice, getRestartApp, setRestartAppFalse
from api import notifyFeelingBad, notifyFeelingHappy, notifyFeelingNeutral
import json
import time
from datetime import datetime
from multiThread import runInNewThread,ReUsableThreadRunner
from serial import getserial
from QueueWorker import QueueWorker

ENV=os.environ.get('ENV')


storage = {}
isWaiterCalled = False
hangoutId=None
callNumber = 1
currentWaiter = None
serviceCallStartTime=None
thr=None
guestCount = None
table=None
waiterId=None
serialNumber=getserial()
pixmap=None
serviceCalls = {}
continueExistingJourney = False
previousJourneyData = None
logoData =None
qWorker = None
lightThreadRunner = None
smileyRunner =  None
restartApplication = False
restaurantChanged = True
smileyTimer =None
askingCable = False
firstJourney = True
smiley = "neutral"
timeOuts = {
    'generalTimeout':60,
    'thankYouTimeout':120,
    'ratingTimeout':300,
    'realTimeExpTimeout':20,
    'waiterMenuTimeout':120
}
def initialize():
    global storage,isWaiterCalled,hangoutId,callNumber,serviceCallStartTime,thr,guestCount,table,waiterId,serialNumber,pixmap,serviceCalls,continueExistingJourney,previousJourneyData,restartApplication,restaurantChanged
    storage.clear()
    isWaiterCalled = False
    hangoutId=None
    callNumber = 1
    serviceCallStartTime=None
    thr=None
    guestCount = None
    table=None
    waiterId=None
    serialNumber=getserial()
    pixmap=None
    serviceCalls.clear()
    continueExistingJourney = False
    previousJourneyData = None
    logoData =None
    restartApplication = False
    
def continueJourneyCheck():
    global continueExistingJourney,previousJourneyData
    exist = isTableOccupied(getTableId())
    previousJourneyData = exist.json()
    if exist.status_code == 409:
        continueExistingJourney = True


def setIcon(button,path):
    button.setIcon(QIcon(path))

def loadPicture(filepath,url):
        
    try:

        data = urllib.request.urlopen(url).read()
        with open(filepath,"wb") as logo:
            logo.write(data)

    except Exception as e:
        with open("logFile.txt","a+") as logFile:
            logFile.write("\n"+str(datetime.now())+" "+"\n"+str(e)+"\n")
        pass
    finally:


        if(url=="" or url==None):
            return None
        with open(filepath,"rb") as logo:
            return logo.read()

def setupKeyboard(self):
    self.key1.clicked.connect(lambda: self.onKey("1"))
    self.key2.clicked.connect(lambda: self.onKey("2"))
    self.key3.clicked.connect(lambda: self.onKey("3"))
    self.key4.clicked.connect(lambda: self.onKey("4"))
    self.key5.clicked.connect(lambda: self.onKey("5"))
    self.key6.clicked.connect(lambda: self.onKey("6"))
    self.key7.clicked.connect(lambda: self.onKey("7"))
    self.key8.clicked.connect(lambda: self.onKey("8"))
    self.key9.clicked.connect(lambda: self.onKey("9"))
    self.key0.clicked.connect(lambda: self.onKey("0"))
    self.key_del.clicked.connect(lambda: self.onKey("x"))

def getTableId ():
    global table
    tableId = table
    try:
        if "tableId" in storage and storage["tableId"] != None:
            tableId = storage["tableId"]
        else:
            tableId = ""
    except Exception as e:
        tableId = ""
        with open("logFile.txt","a+") as logFile:
            logFile.write("\n"+str(datetime.now())+" "+"\n"+str(e)+"\n")
    return tableId

def getRestaurantId ():
    try:
        if "restaurantId" in storage and storage["restaurantId"] != None:
            return storage["restaurantId"]
    except Exception as e:
        with open("logFile.txt","a+") as logFile:
            logFile.write("\n"+str(datetime.now())+" "+"\n"+str(e)+"\n")
        pass
    return None

def saveStorage():
    with open("storage.json", "w") as f:
        json.dump(storage, f)

def loadStorage():
    try:
        with open("storage.json", "r") as f:
            return json.load(f)
    except Exception as e:
        with open("logFile.txt","a+") as logFile:
            logFile.write("\n"+str(datetime.now())+" "+"\n"+str(e)+"\n")
        with open("storage.json", "w") as f:
            json.dump({}, f)
            return {}

def clearStorage():
    global storage
    storage = {}
    saveStorage()

# get current time in seconds
def getCurrentTime():
    import time
    return time.time()


def getHangoutId ():
    # return 4 digit random string
    def getRandomString():
        import random
        return ''.join(random.choice('0123456789') for i in range(4))
    return getRandomString()
    

def yellowLight():
    brightness=127
    if "podBrightness" in storage and storage["podBrightness"] > 0:
        brightness = storage["podBrightness"]
    os.system("sudo python3 /home/pi/waiterlite-raspberry/neopixel-yellow.py " + str(brightness*2))

def blueLight():
    brightness=127
    if "podBrightness" in storage and storage["podBrightness"] > 0:
        brightness = storage["podBrightness"]
    os.system("sudo python3 /home/pi/waiterlite-raspberry/neopixel-blue.py " + str(brightness*2))


def turnOffLight():
    brightness=0
    os.system("sudo python3 /home/pi/waiterlite-raspberry/neopixel-yellow.py " + str(brightness*2))

def neoxPixel(red, green, blue):
    brightness=127
    if "podBrightness" in storage and storage["podBrightness"] > 0:
        brightness = storage["podBrightness"]
    rgba= str(red)+" "+str(green)+" "+str(blue)+" "+str(brightness*2)
    os.system("sudo python3 /home/pi/waiterlite-raspberry/neopixel.py " + rgba)

def whiteLight():
    neoxPixel(255,255,255)

def greenLight():
    neoxPixel(127,255,0)

def navigateToScreen(Screen):
        nextScreen = Screen.getInstance()
        try:
            nextScreen.clear()
        except Exception as e:
            with open("logFile.txt","a+") as logFile:
                logFile.write("\n"+str(datetime.now())+" "+"\n"+str(e)+"\n")
        mainStackedWidget.addWidget(nextScreen)
        mainStackedWidget.setCurrentIndex(mainStackedWidget.currentIndex()+1)
        

def navigateGoBack():
        mainStackedWidget.removeWidget(mainStackedWidget.currentWidget())
        try:
            mainStackedWidget.currentWidget().clear()
        except Exception as e:
            with open("logFile.txt","a+") as logFile:
                logFile.write("\n"+str(datetime.now())+" "+"\n"+str(e)+"\n")
            pass
        

def navigateToRestart():
        # mainStackedWidget.setCurrentIndex(0)
        navigateToScreen(IdleLockScreen)


menuScreenTime = None
isOnMenuScreen = False

def goBackAutomatically():
    if isOnMenuScreen:
        navigateGoBack()
    mainStackedWidget.menuScreenTime.stop()

def goBackToDinerHomeAfter(seconds):
    mainStackedWidget.menuScreenTime = QtCore.QTimer(mainStackedWidget)
    mainStackedWidget.menuScreenTime.setInterval(seconds*1000)
    mainStackedWidget.menuScreenTime.timeout.connect(goBackAutomatically)
    mainStackedWidget.menuScreenTime.start()

def setPixMap(self,path):
    try:
        
        data = "Asdas"
        with open(path,"rb") as logo:
            data =  logo.read()
        image = QImage()
        image.loadFromData(data)
        pixmap = QPixmap(image)
    except Exception as e: 
        pixmap=None
        with open("logFile.txt","a+") as logFile:
                logFile.write("\n"+str(datetime.now())+" "+"\n"+str(e)+"\n")
    self.label_2.setPixmap(pixmap)

def loadLogoPixmap():
    global pixmap,logoData
    try:
        
        data = "Asdas"
        data = loadPicture("restaurantData/logo",storage["restaurantLogo"])
        image = QImage()
        image.loadFromData(data)
        pixmap = QPixmap(image)
    except Exception as e:
        with open("logFile.txt","a+") as logFile:
                logFile.write("\n"+str(datetime.now())+" "+"\n"+str(e)+"\n") 
        pixmap=None
    return pixmap

def renderLogo(self, key="logo", width=220, height=220):
    pixmap = loadLogoPixmap()
    if pixmap != None:
        
        # self.__dict__[key].setPixmap(pixmap)
        # self.__dict__[key].setIcon(QIcon("restaurantData/logo"))
        self.__dict__[key].setStyleSheet(
                    "border-image : url('restaurantData/logo');"
                    "border-top-left-radius :30px;"
                    "border-top-right-radius : 30px; "
                    "border-bottom-left-radius : 30px; "
                    "border-bottom-right-radius : 30px;")
        self.logoBorder.setStyleSheet("border :1.5px solid #D6AD60;"
                    "border-top-left-radius :30px;"
                    "border-top-right-radius : 30px; "
                    "border-bottom-left-radius : 30px; "
                    "border-bottom-right-radius : 30px;")

# class Communicate(QObject):
#     pass






class ReserveScreen(QDialog):
    shared_instance = None
    @staticmethod
    def getInstance():
        if(ReserveScreen.shared_instance == None):
            ReserveScreen.shared_instance = ReserveScreen()
        return ReserveScreen.shared_instance
    def __init__(self):
        super(ReserveScreen, self).__init__()
        loadUi("ui/21ReserveScreen.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToWelcome)
        # runInNewThread(self, self.loadLogo)
        self.loadLogo()
    def loadLogo(self):
        renderLogo(self)
    def clear(self):
        runInNewThread(self,self.loadLogo)
    def navigateToWelcome(self):
        navigateToScreen(WaiterPinScreen)





class IdleLockScreen(QDialog):
    
    
        # runInNewThread(self, self.loadConfigAndLogo)

    shared_instance = None
    @staticmethod
    def getInstance():
        if(IdleLockScreen.shared_instance == None):
            IdleLockScreen.shared_instance = IdleLockScreen()
        return IdleLockScreen.shared_instance

    def __init__(self):
        super(IdleLockScreen, self).__init__()
        loadUi("ui/05IdleLockScreen.ui", self)
        
        self.goToNextButton.clicked.connect(self.navigateToWaiterPinScreen)
        self.appCloseButton.clicked.connect(mainStackedWidget.close)
        
        self.loadConfigAndLogo()  

    def clear(self):
        global serviceCalls,callNumber,smiley
        smiley = "neutral"
        if restaurantChanged:
            self.loadConfigAndLogo()
        try:
            qWorker.addAPICall(self.loadConfigAndLogo,[])
        except Exception as e:
            with open("logFile.txt","a+") as logFile:
                logFile.write("\n"+str(datetime.now())+" "+"\n"+str(e)+"\n")
            pass
        serviceCalls.clear()
        callNumber = 1
        setRestartAppFalse()
        lightThreadRunner.launch(yellowLight)
        
    def loadConfigAndLogo(self):
        loadConfig()
        # pixmap = loadLogoPixmap()
        renderLogo(self, width=220, height=220)
        # self.logo.setPixmap(pixmap.scaled(220, 220))

    def navigateToWaiterPinScreen(self):
        global firstJourney
        if firstJourney:
            navigateToScreen(TableSelectionScreen)
            return
        navigateToScreen(WaiterPinScreen)

class WaiterPinScreen(TimeBoundScreen):
    pin=[]
    signal = pyqtSignal()
    isWrong = False
    shared_instance = None
    @staticmethod
    def getInstance():
        if(WaiterPinScreen.shared_instance == None):
            WaiterPinScreen.shared_instance = WaiterPinScreen()
        return WaiterPinScreen.shared_instance
    def __init__(self):
        super(WaiterPinScreen, self).__init__(timeOuts["generalTimeout"])
        self.pin=[]

        loadUi("ui/06WaiterPinScreen.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToWaiterMenuScreen)
        self.goToConfigButton.clicked.connect(self.navigateToConfigScreen)
        self.signal.connect(self.navigateToIdleLockScreenSlot)
        self.backButton.clicked.connect(self.goBack)
        self.setupKeyboard()
        super().setRunnable(self.navigateToIdleLockScreen,[])
    def goBack(self):
        navigateGoBack()
    @pyqtSlot()
    def navigateToIdleLockScreen(self):
        self.signal.emit()

    def navigateToIdleLockScreenSlot(self):
        navigateToScreen(IdleLockScreen)
        
        
    def setupKeyboard(self):
        setupKeyboard(self)

    def clear(self):
        setPixMap(self,"assets/WaiterLITE-UI-08.png")
        super().reset()
        self.pin.clear() 
        self.renderPin()

    def onKey(self, key):
        global waiterId
        super().reset()
        length=len(self.pin)
        
        if key != "x" :
            if(length<4):
                self.pin.append(key)
                length+=1
            
        else:
            if length>0:
                self.pin.pop()
                length-=1
        
        waiterId=""
        for index in range(4):    
            val=""
            if index < length:
                val=self.pin[index]
                waiterId+=val
            self.__dict__["input_pin_"+str(index)].setText(val)
        if(length==4):
            self.navigateToWaiterMenuScreen()


    def renderPin(self):
        length=len(self.pin)
        
        for index in range(4):    
            val=""
            if index < length:
                val=self.pin[index]
            self.__dict__["input_pin_"+str(index)].setText(val)
        

    
    def navigateToConfirmTable(self):
        super().stop()
        navigateToScreen(ConfirmTable)
        
    def navigateToConfigScreen(self):
        super().stop()
        navigateToScreen(AboutScreen)

    def navigateToWaiterMenuScreen(self):
        global currentWaiter,waiterId
        super().stop()
        
        try:
            thePin = "".join(self.pin)
            if  ("waiters" in storage):
                for waiter in storage["waiters"]:

                    if waiter["referenceId"] == "W"+str(thePin):
                        waiterId = thePin
                        currentWaiter = waiter
                        navigateToScreen(WaiterMenuScreen)
                        return
            self.pin = []
            self.renderPin()
            setPixMap(self,"assets/WaiterLITE-UI-08 2.png")
        except Exception as e:
            with open("logFile.txt","a+") as logFile:
                logFile.write("\n"+str(datetime.now())+" "+"\n"+str(e)+"\n")
            self.pin = []
            self.renderPin()
            setPixMap(self,"assets/WaiterLITE-UI-08 2.png")
         
class WaiterNotExist(TimeBoundScreen):
    pin=[]

    signal = pyqtSignal()
    def __init__(self):
        super(WaiterNotExist, self).__init__(timeOuts["generalTimeout"])
        self.pin=[]
        loadUi("ui/CorrectWaiterPinUIScreen.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToWaiterMenuScreen)
        self.goToConfigButton.clicked.connect(self.navigateToConfigScreen)
        self.signal.connect(self.navigateToIdleLockScreenSlot)
        self.setupKeyboard()
        super().setRunnable(self.navigateToIdleLockScreen,[])

    @pyqtSlot()
    def navigateToIdleLockScreen(self):
        self.signal.emit()

    def navigateToIdleLockScreenSlot(self):
        navigateToScreen(IdleLockScreen)

    def setupKeyboard(self):
        setupKeyboard(self)

    def clear(self):
        super().reset()
        self.pin = []
        self.renderPin()
    def onKey(self, key):
        global waiterId
        super().reset()
        length=len(self.pin)
        if key != "x" :
            if(length<4):
                self.pin.append(key)
                length+=1
        else:
            if length>0:
                self.pin.pop()
                length-=1
        
        
        waiterId=""
        for index in range(4):    
            val=""
            if index < length:
                val=self.pin[index]
                waiterId+=val
            self.__dict__["input_pin_"+str(index)].setText(val)
        if(length==4):
                self.navigateToWaiterMenuScreen()


    def renderPin(self):
        
        length=len(self.pin)
        
        for index in range(4):    
            val=""
            if index < length:
                val=self.pin[index]
            self.__dict__["input_pin_"+str(index)].setText(val)
        

    
    def navigateToConfirmTable(self):
        super().stop()

        navigateToScreen(ConfirmTable)

    def navigateToConfigScreen(self):
        super().stop()
        navigateToScreen(AboutScreen)
    def navigateToWaiterMenuScreen(self):
        global waiterId,currentWaiter
        super().stop()
        try:
            thePin = "".join(self.pin)
            if  ("waiters" in storage):
                for waiter in storage["waiters"]:

                    if waiter["referenceId"] == "W"+str(thePin):
                        waiterId = thePin
                        currentWaiter = waiter
                        navigateToScreen(WaiterMenuScreen)
                        return
            navigateToScreen(WaiterNotExist)
        except Exception as e:
            with open("logFile.txt","a+") as logFile:
                logFile.write("\n"+str(datetime.now())+" "+"\n"+str(e)+"\n")
            navigateToScreen(WaiterNotExist)
              
class AboutScreen(TimeBoundScreen):
    signal = pyqtSignal()
    shared_instance = None
    @staticmethod
    def getInstance():
        if(AboutScreen.shared_instance == None):
            AboutScreen.shared_instance = AboutScreen()
        return AboutScreen.shared_instance
    def __init__(self):
        super(AboutScreen, self).__init__(timeOuts["generalTimeout"])
        loadUi("ui/24AboutScreen.ui", self)
        self.refreshButton.clicked.connect(self.refresh)
        self.backButton.clicked.connect(self.navigateBack)
        self.renderLabels()
        self.signal.connect(self.navigateBackSlot)
        super().setRunnable(self.navigateBack,[])
        self.refreshed = False

    def navigateBack(self):
        self.signal.emit()
    def navigateBackSlot(self):
        super().stop()
        navigateGoBack()
    def clear(self):
        self.refreshed = False
        super().reset()
        setIcon(self.refreshButton,"assets/refreshButton.png")

    def renderLabels(self):
        self.serialLabel.setText(serialNumber)

        if(storage==None):
            self.restaurantLabel.setText("Assign restaurant and table")
            self.brightnessLabel.setText("255")

            return
        if "restauranName" in storage:
            self.restaurantLabel.setText(storage["restauranName"])
        else:
            self.restaurantLabel.setText("Assign restaurant and table")
        if "restauranName" in storage:
            self.tableLabel.setText(storage["tableId"])
        else:
            self.tableLabel.setText("Table Not assigned or no internet")
        
        if "podBrightness" in storage:
            self.brightnessLabel.setText(str(storage["podBrightness"]))
        else: 
            self.brightnessLabel.setText("255")
    
    def refresh(self):
        if(self.refreshed):
            navigateGoBack()
        super().reset()
        restId = getRestaurantId()
        setIcon(self.refreshButton,"assets/refreshDoneButton.png")
        loadConfig()
        self.refreshed = True
        try:
            if(getRestaurantId()!=restId):
                super().stop()
                navigateToScreen(WaiterPinScreen)
        except Exception as e:
            with open("logFile.txt","a+") as logFile:
                logFile.write("\n"+str(datetime.now())+" "+"\n"+str(e)+"\n")
            pass
        self.renderLabels()

        

class ConfirmTable(QDialog):
    shared_instance = None
    @staticmethod
    def getInstance():
        if(ConfirmTable.shared_instance == None):
            ConfirmTable.shared_instance = ConfirmTable()
        return ConfirmTable.shared_instance
    def __init__(self):
        super(ConfirmTable, self).__init__()
        loadUi("ui/07ConfirmTable.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToChooseNumberOfGuests)
        self.clearTableButton.clicked.connect(clearStorage)
    
    def navigateToChooseNumberOfGuests(self):
        navigateToScreen(ChooseNumberOfGuests)

class WaiterMenuScreen(TimeBoundScreen):
    shared_instance = None
    signal = pyqtSignal()
    @staticmethod
    def getInstance():
        if(WaiterMenuScreen.shared_instance == None):
            WaiterMenuScreen.shared_instance = WaiterMenuScreen()
        return WaiterMenuScreen.shared_instance
    def __init__(self):
        super(WaiterMenuScreen, self).__init__(timeOuts["waiterMenuTimeout"])
        loadUi("ui/071WaiterMenuScreen.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToChooseNumberOfGuests)
        self.reserveButton.clicked.connect(self.navigateToReserveScreen)
        self.screenSaverButton.clicked.connect(self.navigateToIdleLockScreen)
        self.clearTableButton.clicked.connect(self.navigateToAboutScreen)
        tableId = getTableId()
        self.signal.connect(self.navigateToIdleLockScreen)
        self.tableSelectionButton.clicked.connect(self.navigateToTableSelectionScreen)
        super().setRunnable(self.navigateToIdleLockScreenEmitter,[])

    def navigateToIdleLockScreenEmitter(self):
        self.signal.emit() 

    def clear(self):
        super().reset()
        tableId = getTableId()
        self.tableNumber.setText(tableId)
        lightThreadRunner.launch(yellowLight)

    def navigateToChooseNumberOfGuests(self):
        super().stop()
        navigateToScreen(ChooseNumberOfGuests)
        
    def navigateToReserveScreen(self):
        super().stop()
        navigateToScreen(ReserveScreen)
    
    def navigateToAboutScreen(self):
        super().stop()
        navigateToScreen(AboutScreen)
    
    def navigateToTableSelectionScreen(self):
        super().stop()
        navigateToScreen(TableSelectionScreen)
    
    def navigateToIdleLockScreen(self):
        super().stop()
        navigateToRestart()

class TableSelectionScreen(QDialog):
    shared_instance = None
    item = None
    @staticmethod
    def getInstance():
        if(TableSelectionScreen.shared_instance == None):
            TableSelectionScreen.shared_instance = TableSelectionScreen()
        return TableSelectionScreen.shared_instance
    def __init__(self):
        super(TableSelectionScreen, self).__init__()
        loadUi("ui/25TableSelectionScreen.ui", self)
        # self.goToNextButton.clicked.connect(self.navigateToWaiterMenuScreen)
        self.listWidget.itemClicked.connect(self.tableSelected)
        self.backButton.clicked.connect(self.navigateGoBackSlot)
        self.confirmSelectionButton.clicked.connect(self.confirmSelection)
        self.listWidget.setStyleSheet(
                                  "QListView"
                                  "{"
                                    "background-color:#041c40;"
                                    "font-size:20px;"
                                    "color:white;"
                                    "border:0px;"
                                  "}"
                                  "QListView::item"
                                  "{"
                                    "background-color: #182e4f;"
                                    "color:white;"
                                    "margin-bottom: 15px;"
                                    "border-radius: 10px;"
                                    "padding: 12px 12px 12px 12px;"
                                    "padding-top:24px;"
                                    "padding-bottom:24px;"
                                  "}"
                                  "QListView::item:selected"
                                  "{"
                                    "background-color: #c09c56;"
                                    "color:#111f2a;"
                                  "}")


        # self.loadTables()
        # runInNewThread(self, self.loadTables)


    def navigateGoBackSlot(self):
        navigateGoBack()

    def clear(self): 
        self.confirmSelectionButton.setVisible(False)
        if firstJourney:
            setPixMap(self,"assets/WaiterLITE-UI-25 1.png")
        else:
            setPixMap(self,"assets/WaiterLITE-UI-25.png")
        self.loadTables()   
    def loadTables(self):
        try:
            
            
            self.listWidget.clear()
            # tables = getAllTables(getRestaurantId())
            
            # tables = getAllTables(restaurantId)

            for t in tables:
                item = QListWidgetItem(t['referenceId'])
                item.setSizeHint(QSize(360, 80))
                self.listWidget.addItem(item)
        except Exception as e:

            tables = storage["tables"]
            for t in tables:
                item = QListWidgetItem(t)
                item.setSizeHint(QSize(364, 80))
                self.listWidget.addItem(item)

    def tableSelected(self,item):
        self.item = item
        self.confirmSelectionButton.setVisible(True)
        print("Set visibles")
    def confirmSelection(self):
        global firstJourney
        try:
            storage["tableId"] = self.item.text()
        except:
            try:
                storage["tableId"] = self.item
            except:
                pass
        saveStorage()

        if firstJourney:
            firstJourney = False
            navigateToScreen(IdleLockScreen)
            return
        self.navigateToWaiterMenuScreen()
        

    def navigateToWaiterMenuScreen(self):

        navigateToScreen(WaiterMenuScreen)
    
    def navigateToIdleLockScreen(self):

        navigateToRestart()
class ContinueExistingJourneyScreen(QDialog):
    shared_instance = None
    @staticmethod
    def getInstance():
        if(ContinueExistingJourneyScreen.shared_instance == None):
            ContinueExistingJourneyScreen.shared_instance = ContinueExistingJourneyScreen()
        return ContinueExistingJourneyScreen.shared_instance
    def __init__(self):
        super(ContinueExistingJourneyScreen, self).__init__()
        loadUi("ui/26ContinueExistingJourney.ui", self)
        self.goToBackButton.clicked.connect(navigateGoBack)
        self.goToContinueHangoutButton.clicked.connect(self.continueExistingJourney)
        self.goToStartHangoutButton.clicked.connect(self.navigateToCheckedIn)
    
    def continueExistingJourney(self):
        global hangoutId,callNumber,serviceCalls,guestCount,previousJourneyData
        callDuration = None
        hangoutId = previousJourneyData["hangoutId"]
        
        guestCount = previousJourneyData["guestCount"]
        try:
            callNumber = previousJourneyData["callNumber"]
        except Exception as e:
            with open("logFile.txt","a+") as logFile:
                logFile.write("\n"+str(datetime.now())+" "+"\n"+str(e)+"\n")
            callNumber = 0
            pass
        try:
            callDuration = previousJourneyData["callDuration"]
            
        except Exception as e:
            with open("logFile.txt","a+") as logFile:
                logFile.write("\n"+str(datetime.now())+" "+"\n"+str(e)+"\n")
            callDuration = 0

        qWorker.addAPICall(changeDevice,[hangoutId])
        if callDuration ==None:
            serviceCalls[callNumber] = {}
            serviceCalls[callNumber]['open'] = time.time()
            navigateToScreen(CloseServiceScreen)
        else:
            callNumber+=1
            navigateToScreen(TapForServiceScreen)
    def navigateToCheckedIn(self):
        global guestCount,waiterId,hangoutId
        qWorker.addAPICall(startHangout,[getTableId(), guestCount, waiterId, hangoutId])
        navigateToScreen(TapForServiceScreen)
class ChooseNumberOfGuests(QDialog):
    global guestCount
    guestCount=""
    shared_instance = None
    @staticmethod
    def getInstance():
        if(ChooseNumberOfGuests.shared_instance == None):
            ChooseNumberOfGuests.shared_instance = ChooseNumberOfGuests()
        return ChooseNumberOfGuests.shared_instance
    def navigateBack(self):
        navigateGoBack()

    def __init__(self):
        super(ChooseNumberOfGuests, self).__init__()
        loadUi("ui/08ChooseNumberOfGuests.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToCheckedInScreen)
        self.goBackButton.clicked.connect(self.navigateBack)

        self.setupKeyboard()    

    


    def setupKeyboard(self):
        setupKeyboard(self)

    def clear(self):
        global guestCount
        setPixMap(self,"assets/WaiterLITE-UI-09-1.png")
        guestCount=""
        countLabel = "10+" if guestCount == "10" else guestCount
        self.__dict__["inputCount"].setText(countLabel)
        global continueExistingJourney
        qWorker.addAPICall(continueJourneyCheck,[])

    def onKey(self, key):
        global guestCount

        if key == "x":
            guestCount=""
        elif key == "0":
            guestCount = "10"
        else:
            guestCount = key
        countLabel = "10+" if guestCount == "10" else guestCount
        self.__dict__["inputCount"].setText(countLabel)



    def navigateToCheckedInScreen(self):

        try: 
            global hangoutId,guestCount,continueExistingJourney,previousJourneyData
            table = getTableId()
            hangoutId = table+ datetime.today().strftime('-%Y-%m-%d-') +getHangoutId()
            serviceCalls['hangoutId'] = hangoutId
            if(guestCount==0 or guestCount==""):
                setPixMap(self,"assets/WaiterLITE-UI-09-2.png")
                return
            if(continueExistingJourney):
                navigateToScreen(ContinueExistingJourneyScreen)
                continueExistingJourney = False
                return
            hangoutId = table+ datetime.today().strftime('-%Y-%m-%d-') +getHangoutId()
            serviceCalls['hangoutId'] = hangoutId
            qWorker.addAPICall(startHangout,[table, guestCount, waiterId, hangoutId])


        except Exception as e:
            with open("logFile.txt","a+") as logFile:
                logFile.write("\n"+str(datetime.now())+" "+"\n"+str(e)+"\n")
            pass
        navigateToScreen(TapForServiceScreen)

class CorrectChooseNumberOfGuests(QDialog):
    global guestCount
    guestCount=""

    def __init__(self):
        super(CorrectChooseNumberOfGuests, self).__init__()
        loadUi("ui/CorrectChooseNumberOfGuests.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToCheckedInScreen)
        self.goBackButton.clicked.connect(self.navigateBack)

        self.setupKeyboard()

    
    def navigateToWaiterMenuScreenSlot(self):
        navigateToScreen(WaiterMenuScreen)
    
    def navigateToWaiterMenuScreen(self):
        self.signal.emit()

    def navigateBack(self):

        navigateGoBack()
    def setupKeyboard(self):
        setupKeyboard(self)

    def clear(self):
        global guestCount

        guestCount=""
        countLabel = "10+" if guestCount == "10" else guestCount
        self.__dict__["inputCount"].setText(countLabel)

    def onKey(self, key):
        global guestCount

        if key == "x":
            guestCount=""
        elif key == "0":
            guestCount = "10"
        else:
            guestCount = key

        countLabel = "10+" if guestCount == "10" else guestCount
        self.__dict__["inputCount"].setText(countLabel)

    def navigateToCheckedInScreen(self):

        try: 
            
            global hangoutId,guestCount
            if(guestCount==0 or guestCount==""):
                return
            table = getTableId()

            hangoutId = table+ datetime.today().strftime('-%Y-%m-%d-') +getHangoutId()
            serviceCalls['hangoutId'] = hangoutId

            # startHangout(table, guestCount, waiterId, hangoutId)
            qWorker.addAPICall(startHangout,[table, guestCount, waiterId, hangoutId])
            # foregroundQueue.enqueue(startHangout,table, guestCount, waiterId, hangoutId,on_failure=startHangoutFailureHandler)
        # try:
            # startHangout(table, guestCount, waiterId, hangoutId)
        # except:
            # multiApiThreadRunner.addAPICall(startHangout,[table, guestCount, waiterId, hangoutId])

        except Exception as e:
            with open("logFile.txt","a+") as logFile:
                logFile.write("\n"+str(datetime.now())+" "+"\n"+str(e)+"\n")
            pass
        navigateToScreen(TapForServiceScreen)




class CheckedInScreen(QDialog):
    shared_instance = None
    @staticmethod
    def getInstance():
        if(CheckedInScreen.shared_instance == None):
            CheckedInScreen.shared_instance = CheckedInScreen()
        return CheckedInScreen.shared_instance
    def __init__(self):
        super(CheckedInScreen, self).__init__()
        loadUi("ui/09CheckedInScreen.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToTapForServiceScreen)
    
    def navigateToTapForServiceScreen(self):
        navigateToScreen(TapForServiceScreen)

class TapForServiceScreen(QDialog):
    shared_instance = None
    @staticmethod
    def getInstance():
        if(TapForServiceScreen.shared_instance == None):
            TapForServiceScreen.shared_instance = TapForServiceScreen()
        return TapForServiceScreen.shared_instance
    previousExperience="Good"
    experience=None

    def __init__(self):
        super(TapForServiceScreen, self).__init__()
        loadUi("ui/10TapForServiceScreen.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToCloseServiceScreen)
        self.menuButton.clicked.connect(self.navigateToDinerActionMenu)
        self.checkoutButton.clicked.connect(self.navigateToCheckoutScreen)
        self.happyButton.clicked.connect(self.notifyHappy)
        self.sadButton.clicked.connect(self.notifySad)
        self.neutralButton.clicked.connect(self.notifyNeutral)
        self.askForCableButton.clicked.connect(self.askForCable)
        self.askedCable = False
        # slider = self.experienceSlider
        # slider.setMinimum(0)
        # slider.setMaximum(10)
        # slider.valueChanged.connect(self.onExperienceChanged)
        # slider.sliderReleased.connect(self.experienceMarked)
    def clear(self):
        global askingCable,smiley
        askingCable = False
        setPixMap(self,"assets/WaiterLITE-UI-13.png")
        setIcon(self.happyButton,"assets/Happy-1.png")
        setIcon(self.sadButton,"assets/sad-1.png")
        setIcon(self.neutralButton,"assets/Average-1.png")

        if smiley == "happy":
            setIcon(self.happyButton,"assets/Happy.png")
        elif smiley =="sad":
            setIcon(self.sadButton,"assets/sad.png")
        elif smiley == "neutral":
            setIcon(self.neutralButton,"assets/Average.png")
        lightThreadRunner.launch(yellowLight)
    def askForCable(self):
        global askingCable
        askingCable = True
        self.navigateToCloseServiceScreen()
    def notifyHappy(self):
        global smiley, hangoutId
        smiley = "happy"
        setIcon(self.happyButton,"assets/Happy.png")
        setIcon(self.sadButton,"assets/sad-1.png")
        setIcon(self.neutralButton,"assets/Average-1.png")
        smileyRunner.addSmiley(notifyFeelingHappy,[hangoutId,waiterId,getRestaurantId(),getTableId()])
    def notifySad(self):
        global smiley, hangoutId
        smiley = "sad"
        setIcon(self.happyButton,"assets/Happy-1.png")
        setIcon(self.sadButton,"assets/sad.png")
        setIcon(self.neutralButton,"assets/Average-1.png")
        smileyRunner.addSmiley(notifyFeelingBad,[hangoutId,waiterId,getRestaurantId(),getTableId()])
    def notifyNeutral(self):
        global smiley, hangoutId
        smiley = "neutral"
        setIcon(self.happyButton,"assets/Happy-1.png")
        setIcon(self.sadButton,"assets/sad-1.png")
        setIcon(self.neutralButton,"assets/Average.png")
        smileyRunner.addSmiley(notifyFeelingNeutral,[hangoutId,waiterId,getRestaurantId(),getTableId()])
    
    def onExperienceChanged(self, value):

        if (value >= 6):
            self.experience = "Good"
        if (value < 6):
            self.experience = "Bad"
    
        


    def experienceMarked(self):
        if(self.previousExperience != self.experience):
            notifyExperience(table, hangoutId, self.experience, self.previousExperience)
            self.previousExperience = self.experience
    
    def navigateToCloseServiceScreen(self):
        self.callWaiter()
        if(getRestartApp()):
            navigateToScreen(IdleLockScreen)
        else:
            navigateToScreen(CloseServiceScreen)
    
    def callWaiter(self):
        try:
            global hangoutId, serviceCallStartTime,table,serviceCalls
            top = len(serviceCalls)
            serviceCalls[callNumber]={}
            serviceCalls[callNumber]['open']=time.time()
            serviceCallStartTime=getCurrentTime()

            qWorker.addAPICall(callWaiter,[getTableId(),  hangoutId,callNumber])
        except:
            with open("logFile.txt","a+") as logFile:
                logFile.write("\n"+str(datetime.now())+" "+"\n"+str(e)+"\n")
            pass
    
    def navigateToDinerActionMenu(self):
        navigateToScreen(DinerActionMenuScreen)
    
    def navigateToCheckoutScreen(self):
        
        navigateToScreen(BillScreen)

class CloseServiceScreen(QDialog):
    shared_instance = None
    @staticmethod
    def getInstance():
        if(CloseServiceScreen.shared_instance == None):
            CloseServiceScreen.shared_instance = CloseServiceScreen()
        return CloseServiceScreen.shared_instance
    def __init__(self):
        super(CloseServiceScreen, self).__init__()
        loadUi("ui/11CloseServiceScreen.ui", self)
        global isWaiterCalled
        isWaiterCalled = True
        self.goToNextButton.clicked.connect(self.navigateToTapForServiceScreen)
        self.menuButton.clicked.connect(self.navigateToDinerActionMenu)
        self.checkoutButton.clicked.connect(self.navigateToCheckoutScreen)
        self.happyButton.clicked.connect(self.notifyHappy)
        self.sadButton.clicked.connect(self.notifySad)
        self.neutralButton.clicked.connect(self.notifyNeutral)
        self.askedCable = False
        # thr.join()
        self.askForCableButton.clicked.connect(self.navigateToTapForServiceScreen)

    def notifyHappy(self):
        global smiley, hangoutId
        smiley = "happy"
        setIcon(self.happyButton,"assets/Happy.png")
        setIcon(self.sadButton,"assets/sad-1.png")
        setIcon(self.neutralButton,"assets/Average-1.png")
        smileyRunner.addSmiley(notifyFeelingHappy,[hangoutId,waiterId,getRestaurantId(),getTableId()])
    def notifySad(self):
        global smiley, hangoutId
        smiley = "sad"
        setIcon(self.happyButton,"assets/Happy-1.png")
        setIcon(self.sadButton,"assets/sad.png")
        setIcon(self.neutralButton,"assets/Average-1.png")
        smileyRunner.addSmiley(notifyFeelingBad,[hangoutId,waiterId,getRestaurantId(),getTableId()])
    def notifyNeutral(self):
        global smiley, hangoutId
        smiley = "neutral"
        setIcon(self.happyButton,"assets/Happy-1.png")
        setIcon(self.sadButton,"assets/sad-1.png")
        setIcon(self.neutralButton,"assets/Average.png")
        smileyRunner.addSmiley(notifyFeelingNeutral,[hangoutId,waiterId,getRestaurantId(),getTableId()])
       
    def clear(self):
        global restartApplication,askingCable,smiley
        
        if(askingCable):
            setPixMap(self,"assets/closeServiceScreenActive.png")
        else:
            setPixMap(self,"assets/WaiterLITE-UI-13-1 2.png")

        self.messageLabel.setText(currentWaiter["firstName"][0:10]+" on the way")
        lightThreadRunner.launch(blueLight)
        setIcon(self.happyButton,"assets/Happy-1.png")
        setIcon(self.sadButton,"assets/sad-1.png")
        setIcon(self.neutralButton,"assets/Average-1.png")
        if smiley == "happy":
            setIcon(self.happyButton,"assets/Happy.png")
        elif smiley =="sad":
            setIcon(self.sadButton,"assets/sad.png")
        elif smiley == "neutral":
            setIcon(self.neutralButton,"assets/Average.png")
        
        

    def navigateToTapForServiceScreen(self):
        # runInNewThread(self, self.waiterArrived)
        self.waiterArrived()
        if(getRestartApp()):
            navigateToRestart()
        else:
            navigateToScreen(TapForServiceScreen)
    
    def waiterArrived(self):
        global isWaiterCalled,callNumber
        try:
            global serviceCalls
            
            serviceCalls[callNumber]['close']=time.time()
            serviceCalls[callNumber]['total'] = serviceCalls[callNumber]['close']-serviceCalls[callNumber]['open']
            
            isWaiterCalled = False
            

            qWorker.addAPICall(waiterArrived,[ getTableId(),hangoutId, callNumber, serviceCalls[callNumber]['total']])
            callNumber = callNumber+1
        except:
            with open("logFile.txt","a+") as logFile:
                logFile.write("\n"+str(datetime.now())+" "+"\n"+str(e)+"\n")
            pass

    
    def navigateToDinerActionMenu(self):
        navigateToScreen(DinerActionMenuScreen)
    
    def navigateToCheckoutScreen(self):
        navigateToScreen(BillScreen)

class DinerActionMenuScreen(TimeBoundScreen):
    
    signal = pyqtSignal()
    shared_instance = None
    @staticmethod
    def getInstance():
        if(DinerActionMenuScreen.shared_instance == None):
            DinerActionMenuScreen.shared_instance = DinerActionMenuScreen()
        return DinerActionMenuScreen.shared_instance
    def __init__(self):
        super(DinerActionMenuScreen, self).__init__(timeOuts["generalTimeout"])
        loadUi("ui/12DinerActionMenuScreen.ui", self)

        self.goBackButton.clicked.connect(self.navigateGoBack)
        self.loadQRCode()
        self.signal.connect(self.navigateGoBackSlot)
        super().setRunnable(self.navigateGoBack,[])

        global isOnMenuScreen
        isOnMenuScreen=True

    
    def clear(self):
        super().reset()
        qWorker.addAPICall(self.loadQRCode,[])

    def navigateGoBack(self):
        self.signal.emit()
    def navigateGoBackSlot(self):
        global isOnMenuScreen
        super().stop()
        isOnMenuScreen=False
        navigateGoBack()

    def loadQRCode(self):

        try:
            url = 'https://i.ibb.co/vh9pSWS/qrcode.png'

            if "menuQr" in storage:
                url = storage["menuQr"] 
                

                data = loadPicture("restaurantData/menuQr",url)

                image = QImage()
                image.loadFromData(data)
                pixmap = QPixmap(image)
                self.qrimage.setPixmap(pixmap.scaled(250, 250))
        except:
            with open("logFile.txt","a+") as logFile:
                logFile.write("\n"+str(datetime.now())+" "+"\n"+str(e)+"\n")
            pass
        

    def navigateToCheckoutScreen(self):
        super().stop()
        navigateToScreen(BillScreen)






class BillScreen(QDialog):
    shared_instance = None
    @staticmethod
    def getInstance():
        if(BillScreen.shared_instance == None):
            BillScreen.shared_instance = BillScreen()
        return BillScreen.shared_instance
    def __init__(self):
        super(BillScreen, self).__init__()
        loadUi("ui/17BillScreen.ui", self)
        self.backButton.clicked.connect(self.navigateBack)
        self.payButton.clicked.connect(self.navigateToPayScreen)
        self.cancelButton.clicked.connect(self.navigateBack)
    
    def navigateBack(self):
        # navigateToScreen(DinerActionMenuScreen)
        navigateGoBack()

    def clear(self):
        lightThreadRunner.launch(yellowLight)

    def navigateToPayScreen(self):
        global table,waiterId,guestCount
        serviceCalls['tableId'] = table
        serviceCalls['waiterId'] = waiterId
        serviceCalls['guestCount'] = guestCount

    
        navigateToScreen(PayQRScreen)
    
    def navigateToFeedbackScreen(self):
        
        navigateToScreen(FeedbackScreen)


class ServerWillAssistScreen(QDialog):
    shared_instance = None
    @staticmethod
    def getInstance():
        if(ServerWillAssistScreen.shared_instance == None):
            ServerWillAssistScreen.shared_instance = ServerWillAssistScreen()
        return ServerWillAssistScreen.shared_instance
    def __init__(self):
        super(ServerWillAssistScreen, self).__init__()
        loadUi("ui/22ServerWillAssist.ui", self)
        self.backButton.clicked.connect(navigateGoBack)
        self.goToNextButton.clicked.connect(self.navigateToThankYouScreen)
        

    
    def navigateToThankYouScreen(self):
        navigateToScreen(ThankYouScreen)

class PayQRScreen(QDialog):
    shared_instance = None
    @staticmethod
    def getInstance():
        if(PayQRScreen.shared_instance == None):
            PayQRScreen.shared_instance = PayQRScreen()
        return PayQRScreen.shared_instance
    def __init__(self):
        super(PayQRScreen, self).__init__()
        loadUi("ui/18PayQRScreen.ui", self)
        self.backButton.clicked.connect(self.navigateBack)
        self.goToNextButton.clicked.connect(self.navigateToThankYouScreen)
        self.loadQRCode()
        # runInNewThread(self, self.loadQRCode)
    
    def clear(self):
        global restaurantChanged
        qWorker.addAPICall(self.loadQRCode,[])
        lightThreadRunner.launch(self.billLight)

    def navigateBack(self):
        navigateGoBack()
    
    def navigateToThankYouScreen(self):
        navigateToScreen(FeedbackScreen)

    def loadQRCode(self):
        try:
            url = 'https://i.ibb.co/vh9pSWS/qrcode.png'
            if "upiQr" in storage:
                url = storage["upiQr"] 
                data = loadPicture("restaurantData/upiQr",url)
                image = QImage()
                image.loadFromData(data)
                pixmap = QPixmap(image)
                self.qrimage.setPixmap(pixmap.scaled(230, 230))
        except:
            with open("logFile.txt","a+") as logFile:
                logFile.write("\n"+str(datetime.now())+" "+"\n"+str(e)+"\n")
            pass
    
    def billLight(self):
        try:
            neoxPixel(255, 45, 208)
        except:
            with open("logFile.txt","a+") as logFile:
                logFile.write("\n"+str(datetime.now())+" "+"\n"+str(e)+"\n")
            pass



class FeedbackScreen(TimeBoundScreen):
    signal = pyqtSignal()
    buttonStyle = "border-width: 2px;border-radius: 35px;padding: 4px;color: white;font-size: 24px;"
    normalStyle = buttonStyle+"background-color: #223757;border-color: #4A5C75;"
    selectedStyle = buttonStyle+"background-color: #D6AD60;border-color: #D6AD60; color: #041c40; font-weight:bold;"
    ratings = {}
    shared_instance = None
    @staticmethod
    def getInstance():
        if(FeedbackScreen.shared_instance == None):
            FeedbackScreen.shared_instance = FeedbackScreen()
        return FeedbackScreen.shared_instance
    def __init__(self):
        super(FeedbackScreen, self).__init__(timeOuts["ratingTimeout"])
        loadUi("ui/19FeedbackScreen.ui", self)
        self.backButton.clicked.connect(self.navigateBack)
        self.goToNextButton.clicked.connect(self.navigateToPaymentOptionScreen)
        
        self.signal.connect(self.endHangoutSlot)

        super().setRunnable(self.endHangout,[])
        
        self.food1.clicked.connect(lambda: self.markRating("food", 1))
        self.food2.clicked.connect(lambda: self.markRating("food", 2))
        self.food3.clicked.connect(lambda: self.markRating("food", 3))
        self.food4.clicked.connect(lambda: self.markRating("food", 4))  
        self.food5.clicked.connect(lambda: self.markRating("food", 5))
        
        self.service1.clicked.connect(lambda: self.markRating("service", 1))
        self.service2.clicked.connect(lambda: self.markRating("service", 2))
        self.service3.clicked.connect(lambda: self.markRating("service", 3))
        self.service4.clicked.connect(lambda: self.markRating("service", 4))
        self.service5.clicked.connect(lambda: self.markRating("service", 5))

        self.ambience1.clicked.connect(lambda: self.markRating("ambience", 1))
        self.ambience2.clicked.connect(lambda: self.markRating("ambience", 2))
        self.ambience3.clicked.connect(lambda: self.markRating("ambience", 3))
        self.ambience4.clicked.connect(lambda: self.markRating("ambience", 4))
        self.ambience5.clicked.connect(lambda: self.markRating("ambience", 5))

        self.music1.clicked.connect(lambda: self.markRating("music", 1))
        self.music2.clicked.connect(lambda: self.markRating("music", 2))
        self.music3.clicked.connect(lambda: self.markRating("music", 3))
        self.music4.clicked.connect(lambda: self.markRating("music", 4))
        self.music5.clicked.connect(lambda: self.markRating("music", 5))
    
    def navigateBack(self):
        super().stop()
        navigateGoBack()

    def markRating(self, type,rating):
        super().reset()

        try:
            if self.ratings[type]==rating:
                self.markRating(type,0)
                return
            else:
                self.ratings[type] = rating
        except Exception as e:
            with open("logFile.txt","a+") as logFile:
                logFile.write("\n"+str(datetime.now())+" "+"\n"+str(e)+"\n")
            self.ratings[type] = rating

        for a in range(5):
            i = a+1
            style = self.selectedStyle if i <= rating else self.normalStyle
            self.__dict__[type+str(i)].setStyleSheet(style)
    def clear(self):
        
        global restartApplication
        super().reset()
        for i in ["food","service","ambience","music"]:
            self.markRating(i,0)
        self.validationLabel.setVisible(False)
        if(getRestartApp()==False):
            pass
        else:
            navigateToRestart()
        # self.ratings.clear()
    def sendRatings(self,ratings):
        try:

            global serviceCalls
            
            ratingKeys = ratings.keys()
            _ratings = map(lambda x: {"ratingType": x.capitalize(), "rating": ratings[x]}, ratingKeys)
            serviceCalls["ratings"] = list(_ratings)
            addMultipleRatings(getTableId(), hangoutId, list(_ratings))

        except:
            with open("logFile.txt","a+") as logFile:
                logFile.write("\n"+str(datetime.now())+" "+"\n"+str(e)+"\n")
            pass
    def tryToSendRatings(self,table,hangout,ratings):
        try:
            addMultipleRatings(table,hangout,ratings)
        except Exception as e:
            with open("logFile.txt","a+") as logFile:
                logFile.write("\n"+str(datetime.now())+" "+"\n"+str(e)+"\n")
            pass
    
    def endHangout(self):
        self.signal.emit()
    def endHangoutSlot(self):
        global callNumber
        
        try:
            if('close' not in serviceCalls[callNumber].keys()):
                qWorker.addAPICall(waiterArrived,[getTableId(),hangoutId,callNumber,time.time()-serviceCalls[callNumber]['open']])
        except Exception as e:
            with open("logFile.txt","a+") as logFile:
                logFile.write("\n"+str(datetime.now())+" "+"\n"+str(e)+"\n")

            pass
        
        callNumber = 1
    
        qWorker.addAPICall(addMultipleRatings,[getTableId(),hangoutId,list([
            {'ratingType':'Food','rating':0},
            {'ratingType':'Music','rating':0},
            {'ratingType':'Service','rating':0},
            {'ratingType':'Ambience','rating':0}
        ])])
        serviceCalls.clear()
        
        lightThreadRunner.launch(yellowLight)
        navigateToScreen(IdleLockScreen)

    def navigateToPaymentOptionScreen(self):

        
        if(len(self.ratings)==4):
            for i in self.ratings:
                if self.ratings[i] ==0:
                    self.validationLabel.setVisible(True)
                    return
            global callNumber
            super().stop()

            hangoutRatings = copy.deepcopy(self.ratings)

            self.ratings.clear()

            ratingKeys = hangoutRatings.keys()
            _ratings = map(lambda x: {"ratingType": x.capitalize(), "rating": hangoutRatings[x]}, ratingKeys)

            
            try:
                if('close' not in serviceCalls[callNumber].keys()):
                    qWorker.addAPICall(waiterArrived,[getTableId(),hangoutId,callNumber,time.time()-serviceCalls[callNumber]['open']])
            except Exception as e:
                with open("logFile.txt","a+") as logFile:
                    logFile.write("\n"+str(datetime.now())+" "+"\n"+str(e)+"\n")

                pass

            callNumber = 1

            
            qWorker.addAPICall(addMultipleRatings,[getTableId(),hangoutId,list(_ratings)])
            serviceCalls.clear()

            lightThreadRunner.launch(yellowLight)
            navigateToScreen(ThankYouScreen)

class SplashScreen(TimeBoundScreen):
    signal = pyqtSignal()
    def __init__(self) :
        super(SplashScreen, self).__init__(1)
        loadUi("ui/Splash.ui",self)
        
        self.signal.connect(self.initialize)
        super().setRunnable(self.initializeEmit,[])
        super().reset()
   
    def initializeEmit(self):
        self.signal.emit()
    def initialize(self):
        global qWorker,lightThreadRunner,smileyRunner
        reserveScreen = ReserveScreen.getInstance()
        waiterPinScreen =  WaiterPinScreen.getInstance()
        aboutScreen = AboutScreen.getInstance()
        confirmTable = ConfirmTable.getInstance()
        waiterMenuScreen =  WaiterMenuScreen.getInstance()
        tableSelectionScreen = TableSelectionScreen.getInstance()
        continueExistingJourneyScreen = ContinueExistingJourneyScreen.getInstance()
        chooseNumberOfGuests =  ChooseNumberOfGuests.getInstance()
        checkedInScreen =  CheckedInScreen.getInstance()
        tapForServiceScreen = TapForServiceScreen.getInstance()
        closeServiceScreen = CloseServiceScreen.getInstance()
        dinerActionMenuScreen = DinerActionMenuScreen.getInstance()
        billScreen = BillScreen.getInstance()
        serverWillAssistScreen =  ServerWillAssistScreen.getInstance()
        payQrscreen = PayQRScreen.getInstance()
        feedbackScreen = FeedbackScreen.getInstance()
        thankYouScreen =  ThankYouScreen.getInstance()
        qWorker = QueueWorker()
        lightThreadRunner = ReUsableThreadRunner()
        smileyRunner = SmileyRunner()

        navigateToScreen(idleLockScreen)
    def clear(self):
        super().reset() 
        # navigateToScreen(IdleLockScreen)
class ThankYouScreen(TimeBoundScreen):
    signal = pyqtSignal()
    shared_instance = None
    @staticmethod
    def getInstance():
        if(ThankYouScreen.shared_instance == None):
            ThankYouScreen.shared_instance = ThankYouScreen()
        return ThankYouScreen.shared_instance
    def __init__(self):
        super(ThankYouScreen, self).__init__(timeOuts["generalTimeout"])
        loadUi("ui/20ThankYouScreen.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToIdleLockScreen)
        self.signal.connect(self.navigateToIdleLockScreenSlot)
        self.loadLogo()
        self.setRunnable(self.navigateToIdleLockScreen,[])
        # runInNewThread(self, self.loadLogo)
    
    def clear(self):
        super().reset()
        qWorker.addAPICall(self.loadLogo,[])

    def loadLogo(self):
        renderLogo(self)
    
    def navigateToIdleLockScreen(self):
        self.signal.emit()
    def navigateToIdleLockScreenSlot(self):
        super().stop()
        navigateToRestart()

def loadConfig():
    global storage, table, restaurantChanged
    try:
        restaurantId = getRestaurantId()
        try:
            table = storage["tableId"]
        except Exception as e:
            with open("logFile.txt","a+") as logFile:
                logFile.write("\n"+str(datetime.now())+" "+"\n"+str(e)+"\n")
            pass
        config = getConfig(serialNumber)
        

        storage = config
        try:
            storage['tableId'] = table
        except Exception as e:
            with open("logFile.txt","a+") as logFile:
                logFile.write("\n"+str(datetime.now())+" "+"\n"+str(e)+"\n")
            pass

        saveStorage()
        newRestId = getRestaurantId()
        if(restaurantId!=newRestId):
            global idleLockScreen,payQRScreen,thankYouScreen,dinerActionMenuScreen
            restaurantChanged = True
            
            
        else:
            restaurantChanged = False

        if(storage['tableId']):
            if(restaurantId!=getRestaurantId() or storage['tableId'] not in storage['tables']):
                storage['tableId'] = storage['tables'][0]
        else:
                storage['tableId'] = storage['tables'][0]
          

    except Exception as e:
        with open("logFile.txt","a+") as logFile:
            logFile.write("\n"+str(datetime.now())+" "+"\n"+str(e)+"\n")
        restaurantChanged = False
        storage=loadStorage()



#Main

MainStyle = """

QPushButton:focus {
    border: 0px;
    outline: none;
}
"""

storage = loadStorage()


app=QApplication(sys.argv)
app.setStyleSheet(MainStyle)
mainStackedWidget=QtWidgets.QStackedWidget()
# idleLockScreen = IdleLockScreen()


idleLockScreen = IdleLockScreen.getInstance()


if ENV == "dev":

    mainwindow=SplashScreen()
else:
    mainwindow=SplashScreen()
mainStackedWidget.addWidget(mainwindow)
mainStackedWidget.setFixedWidth(480)
mainStackedWidget.setFixedHeight(800)

if ENV=='dev':
    mainStackedWidget.show()
else:
    mainStackedWidget.showFullScreen()



signal.signal(signal.SIGINT, signal.SIG_DFL)

try:
    sys.exit(app.exec())
except:
    pass
