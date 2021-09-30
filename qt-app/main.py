import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QDialog
import os 
import signal

isWaiterCalled = False

def yellowLight():
    os.system("sudo python3 /home/pi/scripts/neopixel-yellow.py")

def blueLight():
    os.system("sudo python3 /home/pi/scripts/neopixel.py")

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
        navigateToScreen(CheckedInScreen)

class CheckedInScreen(QDialog):
    def __init__(self):
        super(CheckedInScreen, self).__init__()
        loadUi("ui/09CheckedInScreen.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToTapForServiceScreen)
    
    def navigateToTapForServiceScreen(self):
        navigateToScreen(TapForServiceScreen)

class TapForServiceScreen(QDialog):
    def __init__(self):
        super(TapForServiceScreen, self).__init__()
        loadUi("ui/10TapForServiceScreen.ui", self)
        yellowLight()
        self.goToNextButton.clicked.connect(self.navigateToCloseServiceScreen)
        self.menuButton.clicked.connect(self.navigateToDinerActionMenu)
    
    def navigateToCloseServiceScreen(self):
        navigateToScreen(CloseServiceScreen)
    
    def navigateToDinerActionMenu(self):
        navigateToScreen(DinerActionMenuScreen)

class CloseServiceScreen(QDialog):
    def __init__(self):
        super(CloseServiceScreen, self).__init__()
        loadUi("ui/11CloseServiceScreen.ui", self)
        global isWaiterCalled
        isWaiterCalled = True
        blueLight()
        self.goToNextButton.clicked.connect(self.navigateToTapForServiceScreen)
        self.menuButton.clicked.connect(self.navigateToDinerActionMenu)
    
    def navigateToTapForServiceScreen(self):
        global isWaiterCalled
        isWaiterCalled = False
        navigateToScreen(TapForServiceScreen)
    
    def navigateToDinerActionMenu(self):
        navigateToScreen(DinerActionMenuScreen)

class DinerActionMenuScreen(QDialog):
    def __init__(self):
        super(DinerActionMenuScreen, self).__init__()
        loadUi("ui/12DinerActionMenuScreen.ui", self)
        self.goToNextButton.clicked.connect(self.navigateToQuickMenuScreen)
        self.backButton.clicked.connect(self.navigateBack)
    
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
        # self.goToNextButton.clicked.connect(self.navigateToDrinkItemScreen)
        self.backButton.clicked.connect(self.navigateBack)
    
    def navigateBack(self):
        navigateToScreen(DinerActionMenuScreen)

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
mainwindow=SplashScreen()
mainStackedWidget.addWidget(mainwindow)
mainStackedWidget.setFixedWidth(480)
mainStackedWidget.setFixedHeight(800)
mainStackedWidget.showFullScreen()

signal.signal(signal.SIGINT, signal.SIG_DFL)

try:
    sys.exit(app.exec())
except:
    print("Exiting")