from re import S
import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QDialog, QSlider
import os 
import signal
import urllib.request
import requests
from api import startHangout,callWaiter, waiterArrived, serviceDelayed, notifyExperience
import threading
from subprocess import Popen




isWaiterCalled = False
hangoutId=None
callNumber = 1
serviceCallStartTime=None
thr=None

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
    # os.system("sudo python3 /home/pi/waiterlite-raspberry/neopixel-yellow.py")
    Popen(["sudo", "/usr/bin/python3" "/home/pi/waiterlite-raspberry/neopixel-yellow.py"])
    # time.sleep(2)
    # print("Yellow Light");

def blueLight():
    # os.system("sudo python3 /home/pi/waiterlite-raspberry/neopixel.py")
    Popen(["sudo", "/usr/bin/python3" "/home/pi/waiterlite-raspberry/neopixel.py"])
    # time.sleep(2)
    # print("Blue Light");

def navigateToScreen(Screen):
        nextScreen = Screen()
        mainStackedWidget.addWidget(nextScreen)
        mainStackedWidget.setCurrentIndex(mainStackedWidget.currentIndex()+1)

class SplashScreen(QDialog):
    def __init__(self):
        super(SplashScreen, self).__init__()
        loadUi("ui/Splash.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToWelcome)
    
    def navigateToWelcome(self):
        navigateToScreen(WelcomeScreen)


class WelcomeScreen(QDialog):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("ui/02Welcome.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToWelcome)

    def navigateToWelcome(self):
        navigateToScreen(WifiListScreen)

class WifiListScreen(QDialog):
    def __init__(self):
        super(WifiListScreen, self).__init__()
        loadUi("ui/03WifiList.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToWifiConnected)
    
    def navigateToWifiConnected(self):
        navigateToScreen(WifiConnectedScreen)

class WifiConnectedScreen(QDialog):
    def __init__(self):
        super(WifiConnectedScreen, self).__init__()
        loadUi("ui/04WifiConnectedScreen.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToIdleLockScreen)
    
    def navigateToIdleLockScreen(self):
        navigateToScreen(IdleLockScreen)

class IdleLockScreen(QDialog):
    def __init__(self):
        super(IdleLockScreen, self).__init__()
        loadUi("ui/05IdleLockScreen.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToWaiterPinScreen)
        self.appCloseButton.clicked.connect(mainStackedWidget.close)
    
    def navigateToWaiterPinScreen(self):
        navigateToScreen(WaiterPinScreen)

class WaiterPinScreen(QDialog):
    def __init__(self):
        super(WaiterPinScreen, self).__init__()
        loadUi("ui/06WaiterPinScreen.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToConfirmTable)
    
    def navigateToConfirmTable(self):
        navigateToScreen(ConfirmTable)

class ConfirmTable(QDialog):
    def __init__(self):
        super(ConfirmTable, self).__init__()
        loadUi("ui/07ConfirmTable.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToChooseNumberOfGuests)
    
    def navigateToChooseNumberOfGuests(self):
        navigateToScreen(ChooseNumberOfGuests)

class ChooseNumberOfGuests(QDialog):
    def __init__(self):
        super(ChooseNumberOfGuests, self).__init__()
        loadUi("ui/08ChooseNumberOfGuests.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToCheckedInScreen)
    
    def navigateToCheckedInScreen(self):
        global hangoutId
        hangoutId = "TBCCH-01-2022-06-29-"+getHangoutId()
        startHangout("TBCCH-01", 2, "1111", hangoutId)
        navigateToScreen(CheckedInScreen)

class CheckedInScreen(QDialog):
    def __init__(self):
        super(CheckedInScreen, self).__init__()
        loadUi("ui/09CheckedInScreen.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToTapForServiceScreen)
    
    def navigateToTapForServiceScreen(self):
        navigateToScreen(TapForServiceScreen)

class TapForServiceScreen(QDialog):

    previousExperience="Good"
    experience=None

    def __init__(self):
        super(TapForServiceScreen, self).__init__()
        loadUi("ui/10TapForServiceScreen.ui", self)
        global thr
        thr = threading.Thread(target=yellowLight)
        thr.start()
        self.goToNextButton.clicked.connect(self.navigateToCloseServiceScreen)
        self.menuButton.clicked.connect(self.navigateToDinerActionMenu)
        slider = self.experienceSlider
        slider.setMinimum(0)
        slider.setMaximum(10)
        slider.valueChanged.connect(self.onExperienceChanged)
        slider.sliderReleased.connect(self.experienceMarked)
        thr.join()

    def onExperienceChanged(self, value):
        print(value)
        if (value >= 6):
            self.experience = "Good"
        if (value < 6):
            self.experience = "Bad"

    def experienceMarked(self):
        if(self.previousExperience != self.experience):
            notifyExperience("TBCCH-01", hangoutId, self.experience, self.previousExperience)
            self.previousExperience = self.experience
    
    def navigateToCloseServiceScreen(self):
        global hangoutId, serviceCallStartTime
        serviceCallStartTime=getCurrentTime()
        callWaiter("TBCCH-01", hangoutId, callNumber)
        navigateToScreen(CloseServiceScreen)
    
    def navigateToDinerActionMenu(self):
        navigateToScreen(DinerActionMenuScreen)

class CloseServiceScreen(QDialog):
    def __init__(self):
        super(CloseServiceScreen, self).__init__()
        loadUi("ui/11CloseServiceScreen.ui", self)
        global isWaiterCalled
        isWaiterCalled = True
        thr = threading.Thread(target=blueLight)
        thr.start()
        self.goToNextButton.clicked.connect(self.navigateToTapForServiceScreen)
        self.menuButton.clicked.connect(self.navigateToDinerActionMenu)
        thr.join()
    
    def navigateToTapForServiceScreen(self):
        global isWaiterCalled,callNumber
        isWaiterCalled = False
        waiterArrived("TBCCH-01", hangoutId, callNumber, getCurrentTime()-serviceCallStartTime)
        callNumber = callNumber+1
        navigateToScreen(CloseServiceScreen)
        navigateToScreen(TapForServiceScreen)
    
    def navigateToDinerActionMenu(self):
        navigateToScreen(DinerActionMenuScreen)

class DinerActionMenuScreen(QDialog):
    def __init__(self):
        super(DinerActionMenuScreen, self).__init__()
        loadUi("ui/12DinerActionMenuScreen.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToQuickMenuScreen)
        self.backButton.clicked.connect(self.navigateBack)
        url = 'https://i.ibb.co/vh9pSWS/qrcode.png'
        data = urllib.request.urlopen(url).read()
        image = QImage()
        image.loadFromData(data)
        pixmap = QPixmap(image)
        
        self.qrimage.setPixmap(pixmap.scaled(200, 200))
        # response = requests.get('http://jsonplaceholder.typicode.com/todos/1')
        # title = response.json()['title']
        # self.remoteApiLabel.setText(title);

    
    def navigateToQuickMenuScreen(self):
        navigateToScreen(QuickMenuScreen)
    
    def navigateBack(self):
        global isWaiterCalled
        if isWaiterCalled:
            navigateToScreen(CloseServiceScreen)
        else:
            navigateToScreen(TapForServiceScreen)

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
        navigateToScreen(DinerActionMenuScreen)

    def navigateToDrinkItemScreen(self):
        navigateToScreen(DrinkItemScreen)
    
    def navigateToFoodMenuScreen(self):
        navigateToScreen(FoodMenuScreen)

class DrinkItemScreen(QDialog):
    def __init__(self):
        super(DrinkItemScreen, self).__init__()
        loadUi("ui/14DrinkItemScreen.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToCartScreen)
        self.backButton.clicked.connect(self.navigateBack)
    
    def navigateBack(self):
        navigateToScreen(DinerActionMenuScreen)
    
    def navigateToCartScreen(self):
        navigateToScreen(CartScreen)

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
        navigateToScreen(QuickMenuScreen)

    def navigateToCartScreen(self):
        navigateToScreen(CartScreen)

class CartScreen(QDialog):
    def __init__(self):
        super(CartScreen, self).__init__()
        loadUi("ui/16CartScreen.ui", self)
        self.backButton.clicked.connect(self.navigateBack)
        self.goToNextButton.clicked.connect(self.navigateToBillScreen)
    
    def navigateBack(self):
        navigateToScreen(FoodMenuScreen)

    def navigateToBillScreen(self):
        navigateToScreen(BillScreen)

class BillScreen(QDialog):
    def __init__(self):
        super(BillScreen, self).__init__()
        loadUi("ui/17BillScreen.ui", self)
        self.backButton.clicked.connect(self.navigateBack)
        self.payButton.clicked.connect(self.navigateToPayScreen)
        self.feedbackButton.clicked.connect(self.navigateToFeedbackScreen)
    
    def navigateBack(self):
        navigateToScreen(DinerActionMenuScreen)

    def navigateToPayScreen(self):
        navigateToScreen(PayQRScreen)
    
    def navigateToFeedbackScreen(self):
        navigateToScreen(FeedbackScreen)

class PayQRScreen(QDialog):
    def __init__(self):
        super(PayQRScreen, self).__init__()
        loadUi("ui/18PayQRScreen.ui", self)
        self.backButton.clicked.connect(self.navigateBack)
        self.goToNextButton.clicked.connect(self.navigateToFeedbackScreen)
    
    def navigateBack(self):
        navigateToScreen(DinerActionMenuScreen)
    
    def navigateToFeedbackScreen(self):
        navigateToScreen(FeedbackScreen)

class FeedbackScreen(QDialog):
    def __init__(self):
        super(FeedbackScreen, self).__init__()
        loadUi("ui/19FeedbackScreen.ui", self)
        self.backButton.clicked.connect(self.navigateBack)
        self.goToNextButton.clicked.connect(self.navigateToThankYouScreen)
    
    def navigateBack(self):
        navigateToScreen(PayQRScreen)
    
    def navigateToThankYouScreen(self):
        navigateToScreen(ThankYouScreen)

class ThankYouScreen(QDialog):
    def __init__(self):
        super(ThankYouScreen, self).__init__()
        loadUi("ui/20ThankYouScreen.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToIdleLockScreen)

    
    def navigateToIdleLockScreen(self):
        navigateToScreen(IdleLockScreen)




#Main
app=QApplication(sys.argv)
mainStackedWidget=QtWidgets.QStackedWidget()
mainStackedWidget.setStyleSheet("background-color:rgb(255, 255, 255);")
mainwindow=WelcomeScreen()
mainStackedWidget.addWidget(mainwindow)
mainStackedWidget.setFixedWidth(480)
mainStackedWidget.setFixedHeight(800)
# mainStackedWidget.show()
mainStackedWidget.showFullScreen()

signal.signal(signal.SIGINT, signal.SIG_DFL)

try:
    sys.exit(app.exec())
except:
    print("Exiting")
