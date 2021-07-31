from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, QTimer
from stanag4586edav1.message20000 import Message20000

from .eo_station_widget import Ui_Form

from stanag4586edav1.message_wrapper import *
from stanag4586edav1.message20000 import *
from stanag4586edav1.message20030 import *
from stanag4586edav1.message20040 import *

import time
import asyncio

class C2EoStationWidget(Ui_Form):

    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

    _eo_node = None
    _timer_ptz = None
    _timer_mast = None
    _direction_ptz = UP
    _direction_mast = UP

    _stanag_server = None
    
    def __init__(self, parent=None, eo_node=None, stanag_server=None):
        
        super().setupUi(parent)

        self._stanag_server = stanag_server

        self._eo_node = eo_node
        self._timer_ptz = QTimer()
        self._timer_ptz.timeout.connect(self.timer_ptz_timedout)

        self._timer_mast = QTimer()
        self._timer_mast.timeout.connect(self.timer_mast_timedout)

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

        #video playback controls
        self.btn_play.clicked.connect(lambda: self.playButtonClicked())
        self.btn_stop.clicked.connect(lambda: self.stopButtonClicked())

        #camera ptz controls
        self.btnUp.clicked.connect(lambda: self.up(True))
        self.btnDown.clicked.connect(lambda: self.down(True))
        self.btnLeft.clicked.connect(lambda: self.left(True))
        self.btnRight.clicked.connect(lambda: self.right(True))

        self.btnUp.pressed.connect(lambda: self.ptzButtonPresssed(self.UP))
        self.btnDown.pressed.connect(lambda: self.ptzButtonPresssed(self.DOWN))
        self.btnLeft.pressed.connect(lambda: self.ptzButtonPresssed(self.LEFT))
        self.btnRight.pressed.connect(lambda: self.ptzButtonPresssed(self.RIGHT))

        self.btnUp.released.connect(lambda: self.ptzButtonReleased())
        self.btnDown.released.connect(lambda: self.ptzButtonReleased())
        self.btnLeft.released.connect(lambda: self.ptzButtonReleased())
        self.btnRight.released.connect(lambda: self.ptzButtonReleased())


        #mast controls
        self.btnMastUp.clicked.connect(lambda: self.sendMastUp())
        self.btnMastDown.clicked.connect(lambda: self.sendMastDown())

        self.btnMastUp.pressed.connect(lambda: self.mastButtonPressed(self.UP))
        self.btnMastDown.pressed.connect(lambda: self.mastButtonPressed(self.DOWN))

        self.btnMastUp.released.connect(lambda: self.mastButtonReleased())
        self.btnMastDown.released.connect(lambda: self.mastButtonReleased())


    #Mast related
    def mastButtonPressed(self, direction):
        self._direction_mast = direction
        self._timer_mast.start(100)

    def mastButtonReleased(self):
        self._timer_mast.stop()

    def sendMastUp(self):
        self.sendMastCommand(Message20030.CMD_TYPE_MOVE_UP)

    def sendMastDown(self):
        self.sendMastCommand(Message20030.CMD_TYPE_MOVE_DOWN)

    def timer_mast_timedout(self):
        
        if self._direction_mast is self.UP:
            self.sendMastUp()
        elif self._direction_mast is self.DOWN:
            self.sendMastDown()

    def sendMastCommand(self, cmd_type, absolute_height = 0.0):

        if self._stanag_server is None: return

        msg20030 = Message20030(Message20030.MSGNULL)
        msg20030.time_stamp = 0x00
        msg20030.vehicle_id = self._eo_node.getVehicleId()
        msg20030.cucs_id = 0xA0
        msg20030.station_number = self._eo_node.getStationId()
        msg20030.command_type = cmd_type
        msg20030.absolute_height = absolute_height

        wrapper = MessageWrapper(MessageWrapper.MSGNULL)
        encoded_msg = wrapper.wrap_message(1, 20030, msg20030, False)

        asyncio.get_running_loop().call_soon(self._stanag_server.tx_data, encoded_msg)

    #PTZ Related
    def ptzButtonPresssed(self, direction):
        self._direction_ptz = direction
        self._timer_ptz.start(100)

    def ptzButtonReleased(self):
        self._timer_ptz.stop()
        self.sendStopPtz()
        
    def playButtonClicked(self):
        self._player.play()

    def stopButtonClicked(self):
        self._player.stop()

    def timer_ptz_timedout(self):
        
        if self._direction_ptz is self.UP:
            self.up()
        elif self._direction_ptz is self.DOWN:
            self.down()
        elif self._direction_ptz is self.LEFT:
            self.left()
        elif self._direction_ptz is self.RIGHT:
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

    def sendPtzMessage(self, pan_direction_ptz, tilt_direction_ptz):

        if self._stanag_server is None: return

        msg20000 = Message20000(Message20000.MSGNULL)
        msg20000.time_stamp = 0x00
        msg20000.vehicle_id = self._eo_node.getVehicleId()
        msg20000.cucs_id = 0xA0
        msg20000.station_number = self._eo_node.getStationId()
        msg20000.pan_force = 0.5
        msg20000.pan_direction = pan_direction_ptz
        msg20000.tilt_force = 0.1
        msg20000.tilt_direction = tilt_direction_ptz

        wrapper = MessageWrapper(MessageWrapper.MSGNULL)
        encoded_msg = wrapper.wrap_message(1, 20000, msg20000, False)

        asyncio.get_running_loop().call_soon(self._stanag_server.tx_data, encoded_msg)