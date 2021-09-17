from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QHBoxLayout, QWidget
from PyQt5.QtGui import QIcon
import sys
import os 

def yellowLight():
    os.system("sudo python3 /home/pi/scripts/neopixel-yellow.py")

def blueLight():
    os.system("sudo python3 /home/pi/scripts/neopixel.py")


def window():
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setGeometry(0,0,480,800)
    win.setWindowTitle("Woobly")

    # os.system("sudo python3 /home/pi/scripts/neopixel.py")
    
    window = QWidget()
    btnBlue = QPushButton("Blue")
    btnBlue.setMinimumHeight(100)
    btnBlue.clicked.connect(blueLight)

    

    btnYellow = QPushButton("")
    btnYellow.setMinimumHeight(100)
    btnYellow.clicked.connect(yellowLight)
    btnYellow.setIcon(QIcon('./assets/tap-to-call.png'))
    btnYellow.setGeometry(10,10, 10, 10)

    btnClose = QPushButton("Close")
    btnClose.setMinimumHeight(100)
    btnClose.clicked.connect(window.close)

    # # win.layout.addWidget(btnBlue)

    # layout = QHBoxLayout()
    # layout.addWidget(btnYellow)
    # layout.addWidget(btnBlue)
    # layout.addWidget(QPushButton)

    # win.setLayout(layout)

    
    window.setWindowTitle('Woobly')
    layout = QHBoxLayout()
    layout.addWidget(btnBlue)
    layout.addWidget(btnYellow)
    layout.addWidget(btnClose)
    window.setLayout(layout)
    # window.showFullScreen()


    window.show()
    sys.exit(app.exec())

window()