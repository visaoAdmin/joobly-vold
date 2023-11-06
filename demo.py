from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication,QMainWindow
import sys

def window():
    app = QApplication(sys.argv)
    win =QMainWindow()
    win.setGeometry(10,10,200,200)
    win.setWindowTitle("My first window")
    win.show()
    sys.exit(app.exec_())

window()