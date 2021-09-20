import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QDialog
import os 

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
        self.goToNextButton.clicked.connect(self.navigateToCloseServiceScreen)
    
    def navigateToCloseServiceScreen(self):
        navigateToScreen(CloseServiceScreen)

class CloseServiceScreen(QDialog):
    def __init__(self):
        super(CloseServiceScreen, self).__init__()
        loadUi("ui/11CloseServiceScreen.ui", self)
    #     self.goToNextButton.clicked.connect(self.navigateToCloseServiceScreen)
    
    # def navigateToCloseServiceScreen(self):
    #     navigateToScreen(CloseServiceScreen)



#Main
app=QApplication(sys.argv)
mainStackedWidget=QtWidgets.QStackedWidget()
mainStackedWidget.setStyleSheet("background-color:rgb(255, 255, 255);")
mainwindow=SplashScreen()
mainStackedWidget.addWidget(mainwindow)
mainStackedWidget.setFixedWidth(480)
mainStackedWidget.setFixedHeight(800)
mainStackedWidget.show()

try:
    sys.exit(app.exec())
except:
    print("Exiting")