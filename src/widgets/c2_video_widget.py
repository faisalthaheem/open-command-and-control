from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, QTimer
from stanag4586edav1.message20000 import Message20000

from .video_widget import Ui_Form

from stanag4586edav1.message_wrapper import *
from stanag4586edav1.message20000 import *

import time
import asyncio

class C2VideoWidget(Ui_Form):

    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

    _eo_node = None
    _timer = None
    _direction = UP

    _stanag_server = None
    
    def __init__(self, parent=None, eo_node=None, stanag_server=None):
        
        super().setupUi(parent)

        self._stanag_server = stanag_server

        self._eo_node = eo_node
        self._timer = QTimer()
        self._timer.timeout.connect(self.timer_timedout)

        self.setupMediaPlayer()
        self.setupSlots()


    def setupMediaPlayer(self):

        vw = QVideoWidget()
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        vw.setSizePolicy(sizePolicy)
        self.group_video_vertical_layout.insertWidget(0,vw)

        self._player = QMediaPlayer()
        self._player.setVideoOutput(vw)

        if self._eo_node is None:
            return

        media_uri = "gst-pipeline: rtspsrc location={} latency=0 ! rtph264depay ! avdec_h264 ! videoconvert ! ximagesink name=qtvideosink".format(self._eo_node.getMediaUri())
        self._player.setMedia(QMediaContent(QUrl(media_uri)))

    def setupSlots(self):

        self.btn_play.clicked.connect(lambda: self.playButtonClicked())
        self.btn_stop.clicked.connect(lambda: self.stopButtonClicked())

        self.btnUp.clicked.connect(lambda: self.up(True))
        self.btnDown.clicked.connect(lambda: self.down(True))
        self.btnLeft.clicked.connect(lambda: self.left(True))
        self.btnRight.clicked.connect(lambda: self.right(True))

        self.btnUp.pressed.connect(lambda: self.directionButtonPresssed(self.UP))
        self.btnDown.pressed.connect(lambda: self.directionButtonPresssed(self.DOWN))
        self.btnLeft.pressed.connect(lambda: self.directionButtonPresssed(self.LEFT))
        self.btnRight.pressed.connect(lambda: self.directionButtonPresssed(self.RIGHT))

        self.btnUp.released.connect(lambda: self.directionButtonReleased())
        self.btnDown.released.connect(lambda: self.directionButtonReleased())
        self.btnLeft.released.connect(lambda: self.directionButtonReleased())
        self.btnRight.released.connect(lambda: self.directionButtonReleased())

    def directionButtonPresssed(self, direction):
        self._direction = direction
        self._timer.start(100)

    def directionButtonReleased(self):
        self._timer.stop()
        self.sendStopPtz()
        
    def playButtonClicked(self):
        self._player.play()

    def stopButtonClicked(self):
        self._player.stop()

    def timer_timedout(self):
        
        if self._direction is self.UP:
            self.up()
        elif self._direction is self.DOWN:
            self.down()
        elif self._direction is self.LEFT:
            self.left()
        elif self._direction is self.RIGHT:
            self.right()

    def up(self, sendStop=False):
        print("up")
        self.sendPtzMessage(Message20000.PAN_DIRECTION_NONE, Message20000.TILT_DIRECTION_UP)
        if sendStop: 
            self.sendStopPtzDelayed(0.3)

    def down(self, sendStop=False):
        print("down")
        self.sendPtzMessage(Message20000.PAN_DIRECTION_NONE, Message20000.TILT_DIRECTION_DOWN)
        if sendStop: 
            self.sendStopPtzDelayed(0.3)

    def left(self, sendStop=False):
        print("left")
        self.sendPtzMessage(Message20000.PAN_DIRECTION_LEFT, Message20000.TILT_DIRECTION_NONE)
        if sendStop: 
            self.sendStopPtzDelayed(0.3)

    def right(self, sendStop=False):
        print("right")
        self.sendPtzMessage(Message20000.PAN_DIRECTION_RIGHT, Message20000.TILT_DIRECTION_NONE)
        if sendStop: 
            self.sendStopPtzDelayed(0.3)

    def sendStopPtzDelayed(self, delay=0.0):
        time.sleep(delay)
        asyncio.get_running_loop().call_soon(self.sendStopPtz)

    def sendStopPtz(self):
        self.sendPtzMessage(Message20000.PAN_DIRECTION_NONE, Message20000.TILT_DIRECTION_NONE)

    def sendPtzMessage(self, pan_direction, tilt_direction):

        if self._stanag_server is None: return

        msg20000 = Message20000(Message20000.MSGNULL)
        msg20000.time_stamp = 0x00
        msg20000.vehicle_id = self._eo_node.getVehicleId()
        msg20000.cucs_id = 0xA0
        msg20000.station_number = self._eo_node.getStationId()
        msg20000.pan_force = 0.5
        msg20000.pan_direction = pan_direction
        msg20000.tilt_force = 0.1
        msg20000.tilt_direction = tilt_direction

        wrapper = MessageWrapper(MessageWrapper.MSGNULL)
        encoded_msg = wrapper.wrap_message(1, 20000, msg20000, False)

        asyncio.get_running_loop().call_soon(self._stanag_server.tx_data, encoded_msg)