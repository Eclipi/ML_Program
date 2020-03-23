import sys, time, threading, cv2, traceback, qimage2ndarray
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5 import QtMultimedia, QtMultimediaWidgets
from PyQt5.QtGui import *



class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class MyWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi("pyqttest.ui")
        self.init_ui()

    def init_ui(self):
        self.counter = 0

        self.ui.setWindowTitle("test")
        self.ui.setGeometry(50, 50, 1100, 800)
        # self.ui.pushbtn_connect.clicked(self.start)
        self.ui.frame.setScaledContents(True)
        self.ui.pushbtn_connect.clicked.connect(self.oh_no)
        self.ui.pushbtn_disconnect.clicked.connect(self.stop)
        self.ui.pushbtn_adjust_roi.clicked.connect(self.oh_no2)
        self.ui.lineEdit_x_min.setText("100")
        self.ui.lineEdit_y_min.setText("100")
        self.ui.lineEdit_x_max.setText("200")
        self.ui.lineEdit_y_max.setText("200")

        # self.ui.lineEdit_x_min.textChanged.connect(self.setCoordinate)

        self.threadpool = QThreadPool()

        self.cpt = cv2.VideoCapture(0)
        self.fps = 30
        _, self.img_o = self.cpt.read()
        self.img_o = cv2.cvtColor(self.img_o, cv2.COLOR_RGB2GRAY)

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.recurring_timer)
        self.timer.start()

        self.ui.show()

    def progress_fn(self, n):
        print("%d%% done" % n)

    def execute_this_fn(self, progress_callback):
        for n in range(0, 5):
            time.sleep(1)
            progress_callback.emit(n * 100 / 4)

        return "Done."

    def print_output(self, s):
        print(s)

    def thread_complete(self):
        print("THREAD COMPLETE!")

    def oh_no(self):
        # Pass the function to execute
        worker = Worker(self.nextFrameSlot)  # Any other args, kwargs are passed to the run function
        print("Started")
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)

        # Execute
        self.threadpool.start(worker)
        self.timer.timeout.connect(self.nextFrameSlot)
        self.timer.start(1000 / self.fps)

    def recurring_timer(self):
        self.counter += 1
        # self.l.setText("Counter: %d" % self.counter)

    def start(self):
        # self.th.start()
        # self.th.working = True

        self.timer = QTimer()
        self.timer.timeout.connect(self.oh_no)
        self.timer.start(1000/self.fps)
        print("Started")

    def nextFrameSlot(self, **kwargs):
        _, cam = self.cpt.read()
        # cam = cv2.cvtColor(cam, cv2.COLOR_BGR2RGB)
        # cam = cv2.flip(cam, 1)

        cam2 = cv2.cvtColor(cam, cv2.COLOR_BGR2GRAY)
        MyWindow.canny = cv2.Canny(cam2, 150,200)

        img = QImage(MyWindow.canny, cam.shape[1], cam.shape[0], QImage.Format_Grayscale8)
        pix = QPixmap.fromImage(img)
        self.ui.frame.setPixmap(pix)

    def roiAdjust(self):
        myWindow.x_min = int(self.ui.lineEdit_x_min.text())
        myWindow.y_min = int(self.ui.lineEdit_y_min.text())
        myWindow.x_max = int(self.ui.lineEdit_x_max.text())
        myWindow.y_max = int(self.ui.lineEdit_y_max.text())

    #     print(x_min, x_max, y_min, y_max)
    #
    #     rec = np.zeros((int(x_max)-int(x_min), int(y_max)-int(y_min)), np.uint8)
    #     cv2.rectangle(rec, (x_min,y_min), (x_max,y_max), (0,0,255), 1)
    #
    #     rec = QImage(rec, int(x_max), int(y_max) , QImage.Format_RGB16)
    #     pix2 = QPixmap.fromImage(rec)
    #     self.ui.frame_roi.setPixmap(pix2)

    def oh_no2(self):
        # Pass the function to execute
        worker_2 = Worker(self.nextFrameSlot_roi)  # Any other args, kwargs are passed to the run function
        print("Started")
        worker_2.signals.result.connect(self.print_output)
        worker_2.signals.finished.connect(self.thread_complete)
        worker_2.signals.progress.connect(self.progress_fn)

        # Execute
        self.threadpool.start(worker_2)
        self.timer.timeout.connect(self.nextFrameSlot_roi)
        self.timer.start(1000 / self.fps)

    def displayroi(self):
        # self.th2.start()
        # self.th2.working = True
        self.timer = QTimer()
        self.timer.timeout.connect(self.nextFrameSlot_roi(MyWindow.canny))
        self.timer.start(1000 / self.fps)
        print("roi display")

    def nextFrameSlot_roi(self, **kwargs):
        _, cam = self.cpt.read()
        # cam = cv2.cvtColor(cam, cv2.COLOR_BGR2RGB)
        # cam = cv2.flip(cam, 1)

        self.roiAdjust()
        canny = MyWindow.canny
        sizedimg = canny[self.x_min:self.x_max, self.y_min:self.y_max]
        img_2 = qimage2ndarray.array2qimage(sizedimg)

        pix = QPixmap.fromImage(img_2)
        self.ui.frame_roi.setPixmap(pix)

    def stop(self):
        # self.ui.frame.setPixmap(QPixmap.fromImage(QImage))
        self.timer.stop()
        self.th.working = False
        # self.cpt.release()

    def compare(self, img_o, img_p):
        err = np.sum((img_o.astype("float") - img_p.astype("float")) **2)
        err /= float(img_o.shape[0] * img_p.shape[1])





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
