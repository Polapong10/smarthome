#B6303754 พลพงษ์ นวพงษ์พิพัฒน์
#B6304669 พนิตสุภา อินทรังษี

# Import module
import cv2
from pathlib import Path
import numpy as np
import sys
from time import sleep

# Import module of ultralytics
from ultralytics import YOLO

# Import pyqt5 module
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QObject, QThread, pyqtSignal

# Add Path to the root folder of the project
FILE = Path(__file__).resolve()
ROOT = FILE.parents[0] # Path to the root folder of the project
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

ROOT = str(ROOT)

# Initial UI
from ui.yologui_2 import Ui_MainWindow
app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()

# Initial Counter from OOP module
from customcounter import ObjectCounter
counter = None

# Initial Capture
capVideo = None
global select_mode
select_mode = 0

# QThread for load frame from video
# class UpdateFrameCV2(QObject):
#     frameread = pyqtSignal(np.ndarray)
#     finished = pyqtSignal()

#     def run(self):
#         while capVideo.isOpened():
#             success, frame = capVideo.read()
#             if success:
#                 self.frameread.emit(frame)
#                  # Delay 50 ms for next frame ( 1000 ms / 20 fps = 50 ms )
#                 sleep(0.05)
#             else:
#                 self.finished.emit()
#                 break


class UpdateFrameCV2(QObject):
    frameread = pyqtSignal(np.ndarray)
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.paused = False
        self.mutex = QtCore.QMutex()

    def pause(self):
        with QtCore.QMutexLocker(self.mutex):
            self.paused = True

    def resume(self):
        with QtCore.QMutexLocker(self.mutex):
            self.paused = False

    def run(self):
        while capVideo.isOpened():
            with QtCore.QMutexLocker(self.mutex):
                if self.paused:
                    continue
            success, frame = capVideo.read()
            if success:
                self.frameread.emit(frame)
                # Delay 50 ms for next frame ( 1000 ms / 20 fps = 50 ms )
                sleep(0.05)
            else:
                self.finished.emit()
                break


class mainui(Ui_MainWindow):
    def __init__(self):
        super().setupUi(MainWindow)
        # path video variable
        self.videoDirectory = None
        # path model variable
        self.modelDirectory = None
        # Initial model
        self.model = None
        self.im0d = None
        self.im0_copy = None

        self.threadUpdateFrame = None
        self.workerThreadUpdate = None
        self.pause_sts = False
        # Variable
        self.conf = None
        # Initial button interaction
        self.initialSignal()

    # Initial button interaction
    def initialSignal(self):
        # Load model button
        # self.Loadmodelbt.clicked.connect(self.getDirmodel)
        # # Selected video
        # self.Loadvideobt.clicked.connect(self.getVideoDir)
        # # Start button
        # self.startbt.clicked.connect(self.startCounting)
        self.actionVideo.triggered.connect(self.video_select)
        self.reg_point_slider.valueChanged.connect(self.update_reg)
        self.pushButton.clicked.connect(self.pause_video)
        self.pushButton.setDisabled(True)
        self.conf_slider.valueChanged.connect(self.update_conf)
        self.conf_slider.setValue(2)

    def pause_video(self):
        self.im0_copy = self.im0d.copy()
        self.pause_sts = not self.pause_sts
        if self.pause_sts:
            self.pushButton.setText("Resume")
            if self.workerThreadUpdate:
                self.workerThreadUpdate.pause()
        else:
            if self.workerThreadUpdate:
                self.pushButton.setText("Pause")
                self.workerThreadUpdate.resume()
                self.im0_copy = None
    
    def video_select(self):
        global capVideo
        dialog = QFileDialog()
        pathVideo = dialog.getOpenFileName(MainWindow, 'Selected video file', ROOT, 'Video file (*.mp4 *.mkv *.avi)')[0]
        if pathVideo != '':
            # Store video path
            self.videoDirectory = pathVideo
            self.startCounting()
        else:
            self.videoDirectory = None
            capVideo = None
    def update_conf(self):
        self.conf = float(self.conf_slider.value()/10)
        self.conf_num.setText(str(self.conf))

    def update_reg(self):
        # self.reg_point_slider.value()
        # print(self.qImg.size().width())
        
        try:
            counter.set_arguments(classes_names = self.model.names,
                                    # Point for draw line in counting process
                                    reg_pts = [(int((self.reg_point_slider.value()/100)*self.qImg.size().width()), 0), (int((self.reg_point_slider.value()/100)*self.qImg.size().width()), 1080)],
                                    # Draw track or not
                                    draw_tracks = False
                                    ), 
        except:
            pass
        if self.pause_sts:
            pause_reg_pts = [(int((self.reg_point_slider.value()/100)*self.qImg.size().width()), 0), (int((self.reg_point_slider.value()/100)*self.qImg.size().width()), 1080)]
            for i in range(0, len(pause_reg_pts) - 1, 2):
                self.im0_copy = cv2.line(self.im0_copy, pause_reg_pts[i], pause_reg_pts[i + 1], (255, 0, 255), 2)
            im0_res = cv2.cvtColor(self.im0_copy, cv2.COLOR_BGR2RGB)
            h, w, ch = im0_res.shape
            bytesPerLine = ch * w
            self.qImg = QImage(im0_res.data, w, h, bytesPerLine, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(self.qImg).scaled(self.resultdisplay.size(), QtCore.Qt.KeepAspectRatio)
            self.resultdisplay.setPixmap(pixmap)
            self.im0_copy = self.im0d.copy()
            

    # Start counting
    def startCounting(self):
        self.pushButton.setDisabled(False)
        self.n.setText("0")
        global capVideo
        global counter 
        counter = ObjectCounter()
        if self.videoDirectory is not None:
            # Setup video
            capVideo = cv2.VideoCapture(self.videoDirectory)
            # Setup Model
            self.model = YOLO(r'model/yolov8m.pt')
            # Set QThread
            self.threadUpdateFrame = QThread()
            self.workerThreadUpdate = UpdateFrameCV2()
            self.workerThreadUpdate.moveToThread(self.threadUpdateFrame)
            self.threadUpdateFrame.started.connect(self.workerThreadUpdate.run)
            self.workerThreadUpdate.frameread.connect(self.UpdateCounting)
            self.workerThreadUpdate.finished.connect(self.finishedCounting)
            # Prepair counter arguments
            counter.set_arguments(classes_names = self.model.names,
                                  # Point for draw line in counting process
                                  reg_pts = [(int(capVideo.get(cv2.CAP_PROP_FRAME_WIDTH)*0.625), 0), (int(capVideo.get(cv2.CAP_PROP_FRAME_WIDTH)*0.625), int(capVideo.get(cv2.CAP_PROP_FRAME_HEIGHT)))],
                                  # Draw track or not
                                  draw_tracks = False
                                  ), 
            # self.reg_point_slider.setValue(int((1200/1980)*100))
            # Start detect      
            self.threadUpdateFrame.start()
            self.reg_point_slider.setValue(62)
        else:
            print("Please select model and video file")

    # Update counting
    def UpdateCounting(self, im0):
        # Tracking
        self.im0d = im0.copy()
        im0_tracks = self.model.track(im0, # Image
                                      persist = True, # persisting tracks between frames
                                      save = False, # save results
                                      conf = self.conf, # confidence threshold
                                      classes = 0, # class filter 2 = car
                                      show = False,
                                      device = '0',
                                      verbose = False # show results plot
                                      )
        # Counting
        im0_res = counter.start_counting(im0, im0_tracks)
        # Convert color
        im0_res = cv2.cvtColor(im0_res, cv2.COLOR_BGR2RGB)
        # Display result with Pixmap
        h, w, ch = im0_res.shape
        bytesPerLine = ch * w
        self.qImg = QImage(im0_res.data, w, h, bytesPerLine, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(self.qImg).scaled(self.resultdisplay.size(), QtCore.Qt.KeepAspectRatio)
        self.resultdisplay.setPixmap(pixmap)
        # Update counting display
        self.UpdateCountingDisplay()

    # Update counting display
    def UpdateCountingDisplay(self):
        # Set display
        self.n.setText(str(counter.main_road))


    # Finished counting
    def finishedCounting(self):
        global capVideo
        global counter 
        # Release video
        capVideo.release()
        # Stop QThread
        self.threadUpdateFrame.quit()
        self.threadUpdateFrame.deleteLater
        self.workerThreadUpdate.deleteLater
        # Set text of display result
        self.resultdisplay.setText("Finished counting")
        

if __name__ == '__main__':
    obj = mainui()
    MainWindow.show()
    sys.exit(app.exec_())