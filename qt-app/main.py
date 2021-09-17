from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QHBoxLayout, QWidget
import sys
import os 
import time
from rpi_ws281x import *
import argparse

# LED strip configuration:
LED_COUNT      = 24      # Number of LED pixels.
LED_PIN        = 19      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 1       # set to '1' for GPIOs 13, 19, 41, 45 or 53

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
strip.begin()

def lightUp(color):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i,  color)
        # strip.setPixelColor(i, Color(0, 255, 255) )
        strip.show()


def yellowLight():
    lightUp(Color(250,165,0))

def blueLight():
    lightUp(Color(0,255,255))


def window():
    app = QApplication(sys.argv)
    # win = QMainWindow()
    # win.setGeometry(0,0,480,800)
    # win.setWindowTitle("Yeee")

    # os.system("sudo python3 /home/pi/scripts/neopixel.py")
    
    window = QWidget()

    btnBlue = QPushButton("Blue")
    btnBlue.setMinimumHeight(120)
    btnBlue.clicked.connect(blueLight)

    btnYellow = QPushButton("Yellow")
    btnYellow.setMinimumHeight(120)
    btnYellow.clicked.connect(yellowLight)

    btnClose = QPushButton("Close")
    btnClose.setMinimumHeight(120)
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
    window.showFullScreen()


    # win.show()
    sys.exit(app.exec())

window()