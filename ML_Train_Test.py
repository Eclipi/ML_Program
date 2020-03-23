import sys, time, threading, cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5 import QtMultimedia, QtMultimediaWidgets
from PyQt5.QtGui import *


class MyWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("pyqttest.ui")
        self.init_ui()

    def init_ui(self):
        self.ui.setWindowTitle("test")
        self.ui.setGeometry(50, 50, 1100, 800)
        # self.ui.pushbtn_connect.clicked(self.start)
        self.ui.frame.setScaledContents(True)
        self.ui.pushbtn_connect.clicked.connect(self.start)
        self.ui.pushbtn_disconnect.clicked.connect(self.stop)
        self.ui.pushbtn_adjust_roi.clicked.connect(self.roiAdjust)
        # self.ui.lineEdit_x_min.textChanged.connect(self.setCoordinate)



        self.cpt = cv2.VideoCapture(0)
        self.fps = 30
        _, self.img_o = self.cpt.read()
        self.img_o = cv2.cvtColor(self.img_o, cv2.COLOR_RGB2GRAY)

        self.ui.show()




    def run(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.nextFrameSlot)
        self.timer.start(1000/self.fps)

    def start(self):
        th = QtCore.QThread()
        th.start()

        print("Started")

    def nextFrameSlot(self):
        _, cam = self.cpt.read()
        # cam = cv2.cvtColor(cam, cv2.COLOR_BGR2RGB)
        # cam = cv2.flip(cam, 1)

        cam2 = cv2.cvtColor(cam, cv2.COLOR_BGR2GRAY)
        canny = cv2.Canny(cam2, 150,200)

        img = QImage(canny, cam.shape[1], cam.shape[0], QImage.Format_Grayscale8)
        pix = QPixmap.fromImage(img)
        self.ui.frame.setPixmap(pix)

    # def setCoordinate:
    #

    def roiAdjust(self, img):
        x_min = self.ui.lineEdit_x_min.text()
        y_min = self.ui.lineEdit_y_min.text()
        x_max = self.ui.lineEdit_x_max.text()
        x_max = self.ui.lineEdit_y_max.text()




    def stop(self):
        # self.ui.frame.setPixmap(QPixmap.fromImage(QImage))
        self.timer.stop()
        # self.cpt.release()

    def compare(self, img_o, img_p):
        err = np.sum((img_o.astype("float") - img_p.astype("float")) **2)
        err /= float(img_o.shape[0] * img_p.shape[1])


class Worker(QThread):

    def __init__(self, parent=None):
        super().__init__()
        self.main = parent
        self.working = True

    def __del__(self):
        print("END THREAD")
        self.wait()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # thread = QtCore.QThread()
    # thread.start()
    # vid = ShowVideo()
    # vid.moveToThread(thread)
    #
    # image_viewer1 = ImageViewer()
    #
    # vid.VideoSignal1.connect(image_viewer1.setImage)

    myWindow = MyWindow()
    status = app.exec_()
    sys.exit(status)
