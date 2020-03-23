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

        self.th = Worker(parent=self)
        self.th2 = Worker(parent=self)

        self.cpt = cv2.VideoCapture(0)
        self.fps = 30
        _, self.img_o = self.cpt.read()
        self.img_o = cv2.cvtColor(self.img_o, cv2.COLOR_RGB2GRAY)

        self.ui.show()




    def start(self):
        self.th.start()
        self.th.working = True

        self.timer = QTimer()
        self.timer.timeout.connect(self.nextFrameSlot)
        self.timer.start(1000/self.fps)
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

    def roiAdjust(self, img):
        x_min = int(self.ui.lineEdit_x_min.text())
        y_min = int(self.ui.lineEdit_y_min.text())
        x_max = int(self.ui.lineEdit_x_max.text())
        y_max = int(self.ui.lineEdit_y_max.text())

    #     print(x_min, x_max, y_min, y_max)
    #
    #     rec = np.zeros((int(x_max)-int(x_min), int(y_max)-int(y_min)), np.uint8)
    #     cv2.rectangle(rec, (x_min,y_min), (x_max,y_max), (0,0,255), 1)
    #
    #     rec = QImage(rec, int(x_max), int(y_max) , QImage.Format_RGB16)
    #     pix2 = QPixmap.fromImage(rec)
    #     self.ui.frame_roi.setPixmap(pix2)

    def displayroi(self):
        self.th2.start()
        self.th2.working = True
        self.timer = QTimer()
        self.timer.timeout.connect(self.nextFrameSlot_roi)
        self.timer.start(1000 / self.fps)
        print("roi display")

    def nextFrameSlot_roi(self, canny):
        roi_image = canny[self.x_min:self.x_max, self.y_min,self.y_max]
        pix = QPixmap.fromImage(roi_image)
        self.ui.frame_roi.setPixmap(pix)

    def stop(self):
        # self.ui.frame.setPixmap(QPixmap.fromImage(QImage))
        self.timer.stop()
        self.th.working = False
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
