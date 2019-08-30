from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import cv2, sys, time, os
import numpy as np
from kinectlib.kinectlib import *
from display.detail_form import DetailForm
from display.video_capture import VideoCaptureThread, QVideoWidget
from display.control_window import ControlWindow
from display.pyside_dynamic import loadUiWidget
from display.activity_monitor import ActivityPlotter
from display.viewfinder import ViewfinderWindow
from controller import Controller
import os

from settings import local_path


if __name__ == '__main__':
    app = QApplication(sys.argv)
    #app.setStyle(QStyleFactory.create("Fusion"))
    # initialise another thread for video capture
    video_source = VideoCaptureThread()

    controller = Controller()

    viewfinder = ViewfinderWindow(video_source)

    window = ControlWindow(controller, viewfinder)

    video_source.changeFramePixmap.connect(window.ui.video_rgb.setImage)
    video_source.changeDepthPixmap.connect(window.ui.video_depth.setImage)

    video_source.setParent(window)
    video_source.start()

    window.show()
    viewfinder.show()
    sys.exit(app.exec_())
