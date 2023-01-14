from re import S
import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPixmap, QImage, QColor
from PyQt5.QtWidgets import QApplication, QDialog, QSlider, QListWidget, QListWidgetItem
from PyQt5.QtCore import QSize
import os 
import copy 
import signal
import urllib.request
import requests
from api import startHangout,callWaiter, waiterArrived,sendRatings,sendHangout,startServiceCall,endServiceCall, serviceDelayed, notifyExperience, addMultipleRatings, fetchTableId, getConfig, getAllTables,waiterExists
import threading
from subprocess import Popen
import json
import time
from datetime import datetime
from multiThread import runInNewThread,ReUsableThreadRunner,ServiceCallsSyncer,MultiApiThreadRunner
from serial import getserial

ENV=os.environ.get('ENV')

# print(ENV)

lightThreadRunner = ReUsableThreadRunner()
storage = {}
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
serviceCalls = {}
serviceCallsSyncer = ServiceCallsSyncer()
multiApiThreadRunner = MultiApiThreadRunner("function_queue")
logoData =None




def loadConfig():
    global storage, table
    try:
        config = getConfig(serialNumber)
        # print("Config Loaded", config)
        # if(config == None):
        #     raise Exception("Failed to load")
        storage = config
        storage['tableId'] = table = storage["tables"][0]
        
        # table = storage["tableId"]
        
        # print("Tables",table)
        saveStorage()
    except:
        # storage={}
        # saveStorage()
        print("Failed to load config")

def loadPicture(filepath,url):
        
    try:
        data = urllib.request.urlopen(url).read()
        with open(filepath,"wb") as logo:
            logo.write(data)
    finally:
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
    # print("getTableId")
    # print(storage)
    if "tableId" in storage and storage["tableId"] != None:
        tableId = storage["tableId"]
    else:
        tableId = ""
        # loadConfig()
        # tableId = storage["tableId"]

    return tableId

def getRestaurantId ():
    if "restaurantId" in storage and storage["restaurantId"] != None:
        return storage["restaurantId"]
    return "TBCCH"

def saveStorage():
    with open("storage.json", "w") as f:
        json.dump(storage, f)

def loadStorage():
    try:
        with open("storage.json", "r") as f:
            return json.load(f)
    except:
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
    print("YELLO")
    if "podBrightness" in storage and storage["podBrightness"] > 0:
        brightness = storage["podBrightness"]
    os.system("sudo python3 /home/pi/waiterlite-raspberry/neopixel-yellow.py " + str(brightness*2))
    # Popen("sudo /usr/bin/python3 /home/pi/waiterlite-raspberry/neopixel-yellow.py", shell=True)
    # time.sleep(2)
    print("Yellow Light", brightness)

def blueLight():
    brightness=127
    if "podBrightness" in storage and storage["podBrightness"] > 0:
        brightness = storage["podBrightness"]

    os.system("sudo python3 /home/pi/waiterlite-raspberry/neopixel-blue.py " + str(brightness*2))
    # Popen("sudo /usr/bin/python3 /home/pi/waiterlite-raspberry/neopixel.py", shell=True)
    # time.sleep(2)
    print("Blue Light", brightness)

def turnOffLight():
    brightness=0
    os.system("sudo python3 /home/pi/waiterlite-raspberry/neopixel-yellow.py " + str(brightness*2))
    print("TurnedOff Light", brightness)

def neoxPixel(red, green, blue):
    brightness=127
    if "podBrightness" in storage and storage["podBrightness"] > 0:
        brightness = storage["podBrightness"]
    rgba= str(red)+" "+str(green)+" "+str(blue)+" "+str(brightness*2)
    os.system("sudo python3 /home/pi/waiterlite-raspberry/neopixel.py " + rgba)
    print("Light: RGB", red, green, blue)

def whiteLight():
    neoxPixel(255,255,255)
    print("White Light")
    

def navigateToScreen(Screen):
        nextScreen = Screen
        index = mainStackedWidget.indexOf(nextScreen)
        if(index != -1):
            mainStackedWidget.setCurrentIndex(index)
        else:
            mainStackedWidget.addWidget(nextScreen)
            mainStackedWidget.setCurrentIndex(mainStackedWidget.currentIndex()+1)    

def navigateGoBack():
        mainStackedWidget.removeWidget(mainStackedWidget.currentWidget())

def navigateToRestart():
        # mainStackedWidget.setCurrentIndex(0)
        navigateToScreen(idleLockScreen)


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


def loadLogoPixmap():
    global pixmap,logoData
    if pixmap != None:
        return pixmap
    try:
        
        data = "Asdas"
        data = loadPicture("restaurantData/logo",storage["restaurantLogo"])
        image = QImage()
        image.loadFromData(data)
        pixmap = QPixmap(image)
    except: 
        pixmap=None
    return pixmap

def renderLogo(self, key="logo", width=220, height=220):
    pixmap = loadLogoPixmap()
    if pixmap != None:
        self.__dict__[key].setPixmap(pixmap)




class SplashScreen(QDialog):
    def __init__(self):
        super(SplashScreen, self).__init__()
        loadUi("ui/Splash.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToWelcome)
    
    def navigateToWelcome(self):
        navigateToScreen(welcomeScreen)



class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("ui/02Welcome.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToWelcome)

    def navigateToWelcome(self):
        navigateToScreen(wifiListScreen)

class ReserveScreen(QDialog):
    def __init__(self):
        super(ReserveScreen, self).__init__()
        loadUi("ui/21ReserveScreen.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToWelcome)
        runInNewThread(self, self.loadLogo)
    
    def loadLogo(self):
        renderLogo(self)

    def navigateToWelcome(self):
        navigateToScreen(waiterPinScreen)


class WifiListScreen(QDialog):
    def __init__(self):
        super(WifiListScreen, self).__init__()
        loadUi("ui/03WifiList.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToWifiConnected)
    
    def navigateToWifiConnected(self):
        navigateToScreen(wifiConnectedScreen)


class WifiConnectedScreen(QDialog):
    def __init__(self):
        super(WifiConnectedScreen, self).__init__()
        loadUi("ui/04WifiConnectedScreen.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToIdleLockScreen)
    
    def navigateToIdleLockScreen(self):
        navigateToScreen(idleLockScreen)


class IdleLockScreen(QDialog):
    def __init__(self):
        super(IdleLockScreen, self).__init__()
        loadUi("ui/05IdleLockScreen.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToWaiterPinScreen)
        self.appCloseButton.clicked.connect(mainStackedWidget.close)
        runInNewThread(self, self.loadConfigAndLogo)

    def loadConfigAndLogo(self):
        loadConfig()
        # pixmap = loadLogoPixmap()
        renderLogo(self, width=220, height=220)
        # self.logo.setPixmap(pixmap.scaled(220, 220))

    def navigateToWaiterPinScreen(self):
        navigateToScreen(waiterPinScreen)


class WaiterPinScreen(QDialog):
    pin=[]

    def __init__(self):
        super(WaiterPinScreen, self).__init__()
        self.pin=[]
        loadUi("ui/06WaiterPinScreen.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToWaiterMenuScreen)
        self.setupKeyboard()

    def setupKeyboard(self):
        setupKeyboard(self)

    def onKey(self, key):
        global waiterId
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


    def renderPin(self):
        length=len(self.pin)
        
        for index in range(4):    
            val=""
            if index < length:
                val=self.pin[index]
            self.__dict__["input_pin_"+str(index)].setText(val)

    
    def navigateToConfirmTable(self):
        navigateToScreen(confirmTable)
    
    def navigateToWaiterMenuScreen(self):
        try:
            thePin = "".join(self.pin)
            if  ("waiters" in storage and thePin in storage["waiters"]) or waiterExists(thePin,getRestaurantId()):
                navigateToScreen(waiterMenuScreen)
            else:
                navigateToScreen(waiterNotExist)
        except:
            navigateToScreen(waiterNotExist)

 
class WaiterNotExist(QDialog):
    pin=[]

    def __init__(self):
        super(WaiterNotExist, self).__init__()
        self.pin=[]
        loadUi("ui/CorrectWaiterPinUIScreen.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToWaiterMenuScreen)
        self.setupKeyboard()

    def setupKeyboard(self):
        setupKeyboard(self)

    def onKey(self, key):
        global waiterId
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


    def renderPin(self):
        length=len(self.pin)
        
        for index in range(4):    
            val=""
            if index < length:
                val=self.pin[index]
            self.__dict__["input_pin_"+str(index)].setText(val)

    
    def navigateToConfirmTable(self):
        navigateToScreen(confirmTable)
    
    def navigateToWaiterMenuScreen(self):
        try:
            thePin = "".join(self.pin)
            if  ("waiters" in storage and thePin in storage["waiters"]) or waiterExists(thePin,getRestaurantId()):
                navigateToScreen(waiterMenuScreen)
            else:
                navigateToScreen(waiterNotExist)
        except:
            navigateToScreen(waiterNotExist)
              
waiterNotExist = WaiterNotExist()
class AboutScreen(QDialog):
    def __init__(self):
        super(AboutScreen, self).__init__()
        loadUi("ui/24AboutScreen.ui", self)
        self.refreshButton.clicked.connect(self.refresh)
        self.backButton.clicked.connect(navigateGoBack)
        self.renderLabels()
    
    def renderLabels(self):
        if "restauranName" in storage:
            self.restaurantLabel.setText(storage["restauranName"])
        else:
            self.restaurantLabel.setText("Assign restaurant and table")
        if "restauranName" in storage:
            self.tableLabel.setText(storage["tableId"])
        else:
            self.tableLabel.setText("Table Not assigned or no internet")
        
        self.serialLabel.setText(serialNumber)
        if "podBrightness" in storage:
            self.brightnessLabel.setText(str(storage["podBrightness"]))
        else: 
            self.brightnessLabel.setText("255")
    
    def refresh(self):
        loadConfig()
        self.renderLabels()


      
class ConfirmTable(QDialog):
    def __init__(self):
        super(ConfirmTable, self).__init__()
        loadUi("ui/07ConfirmTable.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToChooseNumberOfGuests)
        self.clearTableButton.clicked.connect(clearStorage)
    
    def navigateToChooseNumberOfGuests(self):
        navigateToScreen(chooseNumberOfGuests)

confirmTable = ConfirmTable()
class WaiterMenuScreen(QDialog):
    def __init__(self):
        super(WaiterMenuScreen, self).__init__()
        loadUi("ui/071WaiterMenuScreen.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToChooseNumberOfGuests)
        self.reserveButton.clicked.connect(self.navigateToReserveScreen)
        self.screenSaverButton.clicked.connect(self.navigateToIdleLockScreen)
        self.clearTableButton.clicked.connect(self.navigateToAboutScreen)
        tableId = getTableId()
        print("Table ID:", tableId)
        self.tableNumber.setText(tableId)
        self.tableSelectionButton.clicked.connect(self.navigateToTableSelectionScreen)
        lightThreadRunner.launch(yellowLight)
    
    def navigateToChooseNumberOfGuests(self):
        navigateToScreen(chooseNumberOfGuests)

    def navigateToReserveScreen(self):
        navigateToScreen(reserveScreen)
    
    def navigateToAboutScreen(self):
        navigateToScreen(aboutScreen)
    
    def navigateToTableSelectionScreen(self):
        navigateToScreen(tableSelectionScreen)
    
    def navigateToIdleLockScreen(self):
        navigateToRestart()

class TableSelectionScreen(QDialog):
    def __init__(self):
        super(TableSelectionScreen, self).__init__()
        loadUi("ui/25TableSelectionScreen.ui", self)
        # self.goToNextButton.clicked.connect(self.navigateToWaiterMenuScreen)
        self.listWidget.itemClicked.connect(self.tableSelected)
        self.backButton.clicked.connect(navigateGoBack)
        runInNewThread(self, self.loadTables)

    
    def loadTables(self):
        try:
            tables = storage["tables"]
            print(tables)
            for t in tables:
                # print(t)
                item = QListWidgetItem(t)
                item.setSizeHint(QSize(400, 60))
                self.listWidget.addItem(item)
        except:
            print("Failed to load tables")

    def tableSelected(self,item):
        storage["tableId"] = item.text()
        #  TODO: ADD send table number to server
        print(storage)
        saveStorage()
        self.navigateToWaiterMenuScreen()
        

    def navigateToWaiterMenuScreen(self):
        navigateToScreen(waiterMenuScreen)
    
    def navigateToIdleLockScreen(self):
        navigateToRestart()
class ChooseNumberOfGuests(QDialog):
    global guestCount
    guestCount=""

    def __init__(self):
        super(ChooseNumberOfGuests, self).__init__()
        loadUi("ui/08ChooseNumberOfGuests.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToCheckedInScreen)
        self.goBackButton.clicked.connect(navigateGoBack)
        self.setupKeyboard()
        
    def setupKeyboard(self):
        setupKeyboard(self)
    
    def onKey(self, key):
        global guestCount
        if key == "x":
            guestCount=""
        elif key == "0":
            guestCount = "10"
        else:
            guestCount = key
        # print("================================",guestCount)
        countLabel = "10+" if guestCount == "10" else guestCount
        self.__dict__["inputCount"].setText(countLabel)

    def navigateToCheckedInScreen(self):
        try: 
            global hangoutId,guestCount
            table = getTableId()
            # print(table)
            hangoutId = table+ datetime.today().strftime('-%Y-%m-%d-') +getHangoutId()
            serviceCalls['hangoutId'] = hangoutId
            startHangout(table, guestCount, waiterId, hangoutId)
        # try:
            # startHangout(table, guestCount, waiterId, hangoutId)
        # except:
            # multiApiThreadRunner.addAPICall(startHangout,[table, guestCount, waiterId, hangoutId])

        except Exception as e:
            print(e)
            print("Failed to startHangout")
        navigateToScreen(tapForServiceScreen)

chooseNumberOfGuests = ChooseNumberOfGuests()
class CheckedInScreen(QDialog):
    def __init__(self):
        super(CheckedInScreen, self).__init__()
        loadUi("ui/09CheckedInScreen.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToTapForServiceScreen)
    
    def navigateToTapForServiceScreen(self):
        navigateToScreen(tapForServiceScreen)

class TapForServiceScreen(QDialog):

    previousExperience="Good"
    experience=None

    def __init__(self):
        super(TapForServiceScreen, self).__init__()
        loadUi("ui/10TapForServiceScreen.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToCloseServiceScreen)
        self.menuButton.clicked.connect(self.navigateToDinerActionMenu)
        self.checkoutButton.clicked.connect(self.navigateToCheckoutScreen)
        # slider = self.experienceSlider
        # slider.setMinimum(0)
        # slider.setMaximum(10)
        # slider.valueChanged.connect(self.onExperienceChanged)
        # slider.sliderReleased.connect(self.experienceMarked)
        lightThreadRunner.launch(yellowLight)

    def onExperienceChanged(self, value):
        print(value)
        if (value >= 6):
            self.experience = "Good"
        if (value < 6):
            self.experience = "Bad"

    def experienceMarked(self):
        if(self.previousExperience != self.experience):
            notifyExperience(table, hangoutId, self.experience, self.previousExperience)
            self.previousExperience = self.experience
    
    def navigateToCloseServiceScreen(self):
        runInNewThread(self, self.callWaiter)
        navigateToScreen(closeServiceScreen)
    
    def callWaiter(self):
        try:
            global hangoutId, serviceCallStartTime,table,serviceCalls
            top = len(serviceCalls)
            serviceCalls[top]={}
            serviceCalls[top]['open']=time.time()
            serviceCallStartTime=getCurrentTime()
            # try:

            callWaiter(table, hangoutId, callNumber)
            # except:
            # multiApiThreadRunner.addAPICall(callWaiter,[getTableId(), hangoutId, callNumber])
        except:
            print("Call Waiter Failed", table, hangoutId, callNumber)
    
    def navigateToDinerActionMenu(self):
        navigateToScreen(dinerActionMenuScreen)
    
    def navigateToCheckoutScreen(self):
        
        navigateToScreen(billScreen)

class CloseServiceScreen(QDialog):
    def __init__(self):
        super(CloseServiceScreen, self).__init__()
        loadUi("ui/11CloseServiceScreen.ui", self)
        global isWaiterCalled
        isWaiterCalled = True
        self.goToNextButton.clicked.connect(self.navigateToTapForServiceScreen)
        self.menuButton.clicked.connect(self.navigateToDinerActionMenu)
        self.checkoutButton.clicked.connect(self.navigateToCheckoutScreen)
        # thr.join()
        lightThreadRunner.launch(blueLight)
    
    def navigateToTapForServiceScreen(self):
        runInNewThread(self, self.waiterArrived)
        navigateToScreen(tapForServiceScreen)
    
    def waiterArrived(self):
        global isWaiterCalled,callNumber
        try:
            global serviceCalls
            top = len(serviceCalls) - 1
            serviceCalls[top]['close']=time.time()
            serviceCalls[top]['total'] = serviceCalls[top]['close']-serviceCalls[top]['open']
            serviceCallStartTime=getCurrentTime()
            isWaiterCalled = False
            # try:
            #     print("waiter arrived")
            waiterArrived(table, hangoutId, callNumber, serviceCalls[top]['total'])
            # except:
            # multiApiThreadRunner.addAPICall(waiterArrived,[getTableId(), hangoutId, callNumber, serviceCalls[top]['total']])
            callNumber = callNumber+1
        except:
            print("Waiter Arrived Failed", table, hangoutId, callNumber, serviceCalls[top]['total'])
    
    def navigateToDinerActionMenu(self):
        navigateToScreen(dinerActionMenuScreen)
    
    def navigateToCheckoutScreen(self):
        navigateToScreen(billScreen)

class DinerActionMenuScreen(QDialog):
    def __init__(self):
        super(DinerActionMenuScreen, self).__init__()
        loadUi("ui/12DinerActionMenuScreen.ui", self)
        # self.goToNextButton.clicked.connect(self.navigateToQuickMenuScreen)
        self.goBackButton.clicked.connect(self.navigateGoBack)
        runInNewThread(self, self.loadQRCode)
        global isOnMenuScreen
        isOnMenuScreen=True
        goBackToDinerHomeAfter(45)

        # self.checkoutButton.clicked.connect(self.navigateToCheckoutScreen)
        # response = requests.get('http://jsonplaceholder.typicode.com/todos/1')
        # title = response.json()['title']
        # self.remoteApiLabel.setText(title);
    
    def navigateGoBack(self):
        global isOnMenuScreen
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
            print("Failed to load Menu QR")
        

    def navigateToCheckoutScreen(self):
        navigateToScreen(billScreen)

    def navigateToQuickMenuScreen(self):
        navigateToScreen(quickMenuScreen)

class QuickMenuScreen(QDialog):
    def __init__(self):
        super(QuickMenuScreen, self).__init__()
        loadUi("ui/13QuickMenuScreen.ui", self)
        self.drinksButton.clicked.connect(self.navigateToDrinkItemScreen)
        self.mainCourseButton.clicked.connect(self.navigateToFoodMenuScreen)
        self.startersButton.clicked.connect(self.navigateToFoodMenuScreen)
        self.chefSpecialsButton.clicked.connect(self.navigateToFoodMenuScreen)
        self.dessertsButton.clicked.connect(self.navigateToFoodMenuScreen)
        self.backButton.clicked.connect(self.navigateBack)
    
    def navigateBack(self):
        navigateToScreen(dinerActionMenuScreen)

    def navigateToDrinkItemScreen(self):
        navigateToScreen(drinkItemScreen)
    
    def navigateToFoodMenuScreen(self):
        navigateToScreen(foodMenuScreen)

class DrinkItemScreen(QDialog):
    def __init__(self):
        super(DrinkItemScreen, self).__init__()
        loadUi("ui/14DrinkItemScreen.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToCartScreen)
        self.backButton.clicked.connect(self.navigateBack)
    
    def navigateBack(self):
        navigateToScreen(dinerActionMenuScreen)
    
    def navigateToCartScreen(self):
        navigateToScreen(cartScreen)

# class FoodMenuScreen(QDialog):
#     def __init__(self):
#         super(FoodMenuScreen, self).__init__()
#         loadUi("ui/15FoodMenuScreen.ui", self)
#         # self.goToNextButton.clicked.connect(self.navigateToDrinkItemScreen)
#         self.backButton.clicked.connect(self.navigateBack)
    
#     def navigateBack(self):
#         navigateToScreen(DinerActionMenuScreen)

class FoodMenuScreen(QDialog):
    def __init__(self):
        super(FoodMenuScreen, self).__init__()
        loadUi("ui/15FoodMenuScreen.ui", self)
        self.backButton.clicked.connect(self.navigateBack)
        self.cartButton.clicked.connect(self.navigateToCartScreen)
        self.goToNextButton.clicked.connect(self.navigateToCartScreen)
    
    def navigateBack(self):
        navigateToScreen(quickMenuScreen)

    def navigateToCartScreen(self):
        navigateToScreen(cartScreen)

class CartScreen(QDialog):
    def __init__(self):
        super(CartScreen, self).__init__()
        loadUi("ui/16CartScreen.ui", self)
        self.backButton.clicked.connect(self.navigateBack)
        self.goToNextButton.clicked.connect(self.navigateToBillScreen)
    
    def navigateBack(self):
        navigateToScreen(foodMenuScreen)

    def navigateToBillScreen(self):
        navigateToScreen(billScreen)

class BillScreen(QDialog):
    def __init__(self):
        super(BillScreen, self).__init__()
        loadUi("ui/17BillScreen.ui", self)
        self.backButton.clicked.connect(self.navigateBack)
        self.payButton.clicked.connect(self.navigateToPayScreen)
        self.cancelButton.clicked.connect(self.navigateBack)
    
    def navigateBack(self):
        # navigateToScreen(DinerActionMenuScreen)
        navigateGoBack()

    def navigateToPayScreen(self):
        global table,waiterId,guestCount
        serviceCalls['tableId'] = table
        serviceCalls['waiterId'] = waiterId
        serviceCalls['guestCount'] = guestCount
        # print(serviceCalls)
        # serviceCallsSyncer.addServiceCall(copy.deepcopy(serviceCalls))
       
        serviceCalls.clear()
    
        navigateToScreen(payQRScreen)
    
    def navigateToFeedbackScreen(self):
        
        navigateToScreen(feedbackScreen)

class PaymentOptionsScreen(QDialog):
    def __init__(self):
        super(PaymentOptionsScreen, self).__init__()
        loadUi("ui/23PaymentOptionsScreen.ui", self)
        self.backButton.clicked.connect(navigateGoBack)
        self.cardButton.clicked.connect(self.navigateToServerWillAssistScreen)
        self.cashButton.clicked.connect(self.navigateToServerWillAssistScreen)
        self.scanButton.clicked.connect(self.navigateToUpiScreen)


    
    def navigateToServerWillAssistScreen(self):
        navigateToScreen(serverWillAssistScreen)
    
    def navigateToUpiScreen(self):
        navigateToScreen(payQRScreen)

class ServerWillAssistScreen(QDialog):
    def __init__(self):
        super(ServerWillAssistScreen, self).__init__()
        loadUi("ui/22ServerWillAssist.ui", self)
        self.backButton.clicked.connect(navigateGoBack)
        self.goToNextButton.clicked.connect(self.navigateToThankYouScreen)
        

    
    def navigateToThankYouScreen(self):
        navigateToScreen(thankYouScreen)

class PayQRScreen(QDialog):
    def __init__(self):
        super(PayQRScreen, self).__init__()
        loadUi("ui/18PayQRScreen.ui", self)
        self.backButton.clicked.connect(self.navigateBack)
        self.goToNextButton.clicked.connect(self.navigateToThankYouScreen)
        runInNewThread(self, self.loadQRCode)
        lightThreadRunner.launch(self.billLight)
    
    def navigateBack(self):
        navigateGoBack()
    
    def navigateToThankYouScreen(self):
        navigateToScreen(feedbackScreen)

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
            print("Failed to load upi QR")
    
    def billLight(self):
        try:
            neoxPixel(255, 45, 208)
        except:
            print("Failed to turn bill light")


class FeedbackScreen(QDialog):
    buttonStyle = "border-width: 2px;border-radius: 35px;padding: 4px;color: white;font-size: 24px;"
    normalStyle = buttonStyle+"background-color: #223757;border-color: #4A5C75;"
    selectedStyle = buttonStyle+"background-color: #D6AD60;border-color: #D6AD60;"
    ratings = {}

    def __init__(self):
        super(FeedbackScreen, self).__init__()
        loadUi("ui/19FeedbackScreen.ui", self)
        self.backButton.clicked.connect(self.navigateBack)
        self.goToNextButton.clicked.connect(self.navigateToPaymentOptionScreen)
        
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
        navigateGoBack()

    def markRating(self, type,rating):
        # print(rating)
        self.ratings[type] = rating
        for a in range(5):
            i = a+1
            style = self.selectedStyle if i <= rating else self.normalStyle
            self.__dict__[type+str(i)].setStyleSheet(style)
    
    def sendRatings(self,ratings):
        try:
            # print("Ratings Data", ratings)
            global serviceCalls
            
            ratingKeys = ratings.keys()
            _ratings = map(lambda x: {"ratingType": x.capitalize(), "rating": ratings[x]}, ratingKeys)
            serviceCalls["ratings"] = list(_ratings)
            addMultipleRatings(getTableId(), hangoutId, list(_ratings))
            # self.ratings={}
            # print("New Ratings Data"ratings)
        except:
            print("Rating Failed", list(ratings))
    def tryToSendRatings(self,table,hangout,ratings):
        try:
            addMultipleRatings(table,hangout,ratings)
        except Exception as e:
            print("Error",e)
            pass
        
    def navigateToPaymentOptionScreen(self):
        # print("prev self.ratings", self.ratings)
        
        if(len(self.ratings)==4):
            global callNumber
            # print("self.ratings", self.ratings)
            hangoutRatings = copy.deepcopy(self.ratings)
            # print("hangoutRatings", hangoutRatings)
            self.ratings.clear()
            # print("new self.ratings", self.ratings, hangoutRatings)
            ratingKeys = hangoutRatings.keys()
            _ratings = map(lambda x: {"ratingType": x.capitalize(), "rating": hangoutRatings[x]}, ratingKeys)
            callNumber = 1
        # try:
        #     print(list(_ratings)) 
            # addMultipleRatings(table,hangoutId,list(_ratings))
        # except:
            # multiApiThreadRunner.addAPICall(addMultipleRatings,[table,hangoutId,list(_ratings)])
            
    
            runInNewThread(self, lambda:self.tryToSendRatings(table,hangoutId,list(_ratings)))
            lightThreadRunner.launch(yellowLight)
            navigateToScreen(thankYouScreen)

class ThankYouScreen(QDialog):
    def __init__(self):
        super(ThankYouScreen, self).__init__()
        loadUi("ui/20ThankYouScreen.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToIdleLockScreen)
        runInNewThread(self, self.loadLogo)
    
    def loadLogo(self):
        renderLogo(self)
    
    def navigateToIdleLockScreen(self):
        navigateToRestart()



#Main

MainStyle = """

QPushButton:focus {
    border: 0px;
    outline: none;
}
"""

storage = loadStorage()
print(storage)

app=QApplication(sys.argv)
app.setStyleSheet(MainStyle)
mainStackedWidget=QtWidgets.QStackedWidget()



if ENV == "dev":
    #if start any other screen change this.
    mainwindow=IdleLockScreen()
else:
    mainwindow=IdleLockScreen()
mainStackedWidget.addWidget(mainwindow)
mainStackedWidget.setFixedWidth(480)
mainStackedWidget.setFixedHeight(800)

if ENV=='dev':
    mainStackedWidget.show()
else:
    mainStackedWidget.showFullScreen()



signal.signal(signal.SIGINT, signal.SIG_DFL)

try:
    cartScreen = CartScreen()
    foodMenuScreen = FoodMenuScreen()
    drinkItemScreen = DrinkItemScreen()
    quickMenuScreen = QuickMenuScreen()
    dinerActionMenuScreen = DinerActionMenuScreen()
    closeServiceScreen = CloseServiceScreen()
    checkedInScreen = CheckedInScreen()
    reserveScreen = ReserveScreen()
    wifiListScreen = WifiListScreen()
    wifiConnectedScreen = WifiConnectedScreen()
    idleLockScreen = IdleLockScreen()
    waiterPinScreen = WaiterPinScreen()
    tapForServiceScreen = TapForServiceScreen()

    tableSelectionScreen = TableSelectionScreen()
    waiterMenuScreen  = WaiterMenuScreen()
    aboutScreen = AboutScreen() 
    paymentOptionsScreen = PaymentOptionsScreen()

    payQRScreen = PayQRScreen()
    serverWillAssistScreen = ServerWillAssistScreen()

    splashScreen = SplashScreen()
    thankYouScreen = ThankYouScreen()
    feedbackScreen = FeedbackScreen()

    billScreen = BillScreen()
    sys.exit(app.exec())
    

except:
    print("Exiting")