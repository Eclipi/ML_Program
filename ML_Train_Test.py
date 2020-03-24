import sys, time, threading, cv2, qimage2ndarray, os
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5 import QtMultimedia, QtMultimediaWidgets
from PyQt5.QtGui import *


class MyWindow(QWidget):
    x_min = 225
    y_min = 325
    x_max = 325
    y_max = 425
    canny_threshold1 = 50
    canny_threshold2 = 250

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
        self.ui.pushbtn_adjust_threshold.clicked.connect(self.thresholdAdjust)
        self.ui.pushbtn_select_folder.clicked.connect(self.selectFolder)
        self.ui.pushbtn_taking_train_pics.clicked.connect(self.takingPictures)

        self.ui.lineEdit_x_min.setText(str(self.x_min))
        self.ui.lineEdit_y_min.setText(str(self.y_min))
        self.ui.lineEdit_x_max.setText(str(self.x_max))
        self.ui.lineEdit_y_max.setText(str(self.y_max))
        self.ui.lineEdit_threshold_1.setText(str(self.canny_threshold1))
        self.ui.lineEdit_threshold_2.setText(str(self.canny_threshold2))


        # self.ui.lineEdit_x_min.textChanged.connect(self.setCoordinate)

        self.th = Worker(parent=self)
        self.th2 = Worker(parent=self)

        self.cpt = cv2.VideoCapture(0)
        self.fps = 30
        _, self.img_o = self.cpt.read()
        self.img_o = cv2.cvtColor(self.img_o, cv2.COLOR_RGB2GRAY)

        self.ui.show()

# 카메라 쓰레드 시작
    def start(self):
        self.th.start()
        self.th.working = True

        self.timer = QTimer()
        self.timer.timeout.connect(self.nextFrameSlot)
        self.timer.start(1000/self.fps)
        print("Started")

#ROI 값 변경
    def roiAdjust(self, img):
        myWindow.x_min = int(self.ui.lineEdit_x_min.text())
        myWindow.y_min = int(self.ui.lineEdit_y_min.text())
        myWindow.x_max = int(self.ui.lineEdit_x_max.text())
        myWindow.y_max = int(self.ui.lineEdit_y_max.text())

#OpenCV로 카메라 불러오기
    def nextFrameSlot(self):
        _, cam = self.cpt.read()
        # cam = cv2.cvtColor(cam, cv2.COLOR_BGR2RGB)
        # cam = cv2.flip(cam, 1)

        cam2 = cv2.cvtColor(cam, cv2.COLOR_BGR2GRAY)
        canny = cv2.Canny(cam2, self.canny_threshold1,self.canny_threshold2)

        sizedimg = canny[self.x_min:self.x_max, self.y_min:self.y_max]
        img_2 = qimage2ndarray.array2qimage(sizedimg)

        pix2 = QPixmap.fromImage(img_2)

        img = QImage(canny, cam.shape[1], cam.shape[0], QImage.Format_Grayscale8)

        pix = QPixmap.fromImage(img)
        self.ui.frame.setPixmap(pix)
        self.ui.frame_roi.setPixmap(pix2)

#Canny Threshold값 변경
    def thresholdAdjust(self):
        myWindow.canny_threshold1 = int(self.ui.lineEdit_threshold_1.text())
        myWindow.canny_threshold2 = int(self.ui.lineEdit_threshold_2.text())

#카메라 쓰레드 정지
    def stop(self):
        # self.ui.frame.setPixmap(QPixmap.fromImage(QImage))
        self.timer.stop()
        self.th.working = False
        # self.cpt.release()

    def selectFolder(self):
        MyWindow.fname = QFileDialog.getExistingDirectory(self)
        print("Directory is: ", self.fname)

    def takingPictures(self):
        new_folder_directory = self.fname + "/" + self.ui.lineEdit_amount.text()
        new_folder_directory = str(new_folder_directory)
        print(new_folder_directory)
        try:
            if not os.path.exists(new_folder_directory):
                os.makedirs(new_folder_directory)
        except OSError:
            print("Failed to create directory!" + new_folder_directory)

        directory = self.fname + "/" + self.ui.lineEdit_amount.text()
        print(directory)

#쓰레드 클레스
class Worker(QThread):

    def __init__(self, parent=None):
        super().__init__()
        self.main = parent
        self.working = True

    def __del__(self):
        print("END THREAD")
        self.wait()

    def run(self):
        print("thread start")
        time.sleep(5)
        print("thread complete")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    status = app.exec_()
    sys.exit(status)
