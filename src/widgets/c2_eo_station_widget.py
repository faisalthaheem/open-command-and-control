from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, QTimer
from PyQt5.QtCore import pyqtSlot

from stanag4586edav1.message20000 import Message20000

from .eo_station_widget import Ui_Form

from stanag4586edav1.message_wrapper import *
from stanag4586edav1.message20000 import *
from stanag4586edav1.message20030 import *
from stanag4586edav1.message20040 import *
from stanag4586edav1.message200 import *
from stanag4586edav1.message201 import *
from stanag4586edav1.message302 import *

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
    _timer_zoom = None
    
    _direction_ptz = UP
    _direction_mast = UP
    _cmd_zoom = Message200.SET_ZOOM_STOP_ZOOM

    _stanag_server = None

    _last_known_zoom = 0.05
    
    def __init__(self, parent=None, eo_node=None, stanag_server=None, vehicle_data_model=None):
        
        super().setupUi(parent)

        self._stanag_server = stanag_server
        self._eo_node = eo_node
        self._vehicle_data_model = vehicle_data_model

        self._timer_ptz = QTimer()
        self._timer_ptz.timeout.connect(self.timer_ptz_timedout)

        self._timer_mast = QTimer()
        self._timer_mast.timeout.connect(self.timer_mast_timedout)

        self._timer_zoom = QTimer()
        self._timer_zoom.timeout.connect(self.timer_zoom_timeout)

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
        self._player.play()

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

        #lrf controls
        self.cmd_lrf_off.clicked.connect(lambda: self.sendLrfCommand(Message201.LRF_OFF))
        self.cmd_lrf_on.clicked.connect(lambda: self.sendLrfCommand(Message201.LRF_ON_SAFE))
        self.cmd_lrf_arm.clicked.connect(lambda: self.sendLrfCommand(Message201.LRF_ARM))
        self.cmd_lrf_fire.clicked.connect(lambda: self.sendLrfCommand(Message201.LRF_FIRE_ONE_PULSE))

        #zoom controls
        self.cmd_zoom_in.clicked.connect(lambda: self.zoomInOnce())
        self.cmd_zoom_out.clicked.connect(lambda: self.zoomOutOnce())

        self.cmd_zoom_in.pressed.connect(lambda: self.sendRepeatZoomCmd(Message200.SET_ZOOM_ZOOM_IN))
        self.cmd_zoom_out.pressed.connect(lambda: self.sendRepeatZoomCmd(Message200.SET_ZOOM_ZOOM_OUT))

        self.cmd_zoom_in.released.connect(lambda: self.sendRepeatZoomCmd(Message200.SET_ZOOM_STOP_ZOOM))
        self.cmd_zoom_out.released.connect(lambda: self.sendRepeatZoomCmd(Message200.SET_ZOOM_STOP_ZOOM))

        #for status messages
        self._vehicle_data_model.onMastStatusReceived.connect(self.onMastStatusReceived)
        self._vehicle_data_model.onEoLrfStatusReceived.connect(self.onEoLrfStatusReceived)
    
    #############
    ## Zoom Related
    def zoomInOnce(self):
        #take last known zoom value, add/subract and send cmd through sendzoomcmdutil
        if self._last_known_zoom - 0.05 >= 0.05:
            self._cmd_zoom = Message200.SET_ZOOM_USE_HV_FOV
            self.sendZoomCmd(self._last_known_zoom - 0.05)


    def zoomOutOnce(self):
        if self._last_known_zoom + 0.05 < 3.14:
            self._cmd_zoom = Message200.SET_ZOOM_USE_HV_FOV
            self.sendZoomCmd(self._last_known_zoom + 0.05)

    def zoomStop(self):
        self._cmd_zoom = Message200.SET_ZOOM_STOP_ZOOM
        self.sendZoomCmd()

    def sendRepeatZoomCmd(self, cmd):
        self._cmd_zoom = cmd

        if cmd == Message200.SET_ZOOM_STOP_ZOOM:
            self._timer_zoom.stop()
            self.zoomStop()    
        else:
            self._timer_zoom.start(100)

    def timer_zoom_timeout(self):
        self.sendZoomCmd()

    def sendZoomCmd(self, h_fov_to_set = 0.05):
        
        msg200 = Message200(Message200.MSGNULL)

        # Zoom specific fields
        msg200.set_zoom = self._cmd_zoom

        if self._cmd_zoom != Message200.SET_ZOOM_USE_HV_FOV:
            msg200.set_horizontal_fov = 0.05
            msg200.set_vertical_fov = 0.05
        else:
            msg200.set_horizontal_fov = h_fov_to_set
            msg200.set_vertical_fov = 0.05

        # Other fields
        msg200.time_stamp = 0x00
        msg200.vehicle_id = self._eo_node.getVehicleId()
        msg200.cucs_id = 0xA0
        msg200.station_number = self._eo_node.getStationId()
        msg200.set_centreline_azimuth_angle = -1000.0
        msg200.set_centreline_elevation_angle = -1000.0
        msg200.horizontal_slew_rate = 0.0
        msg200.vertical_slew_rate = 0.0
        msg200.latitude = 0.0
        msg200.longitude = 0.0
        msg200.altitude = 0.0
        msg200.altitude_type = Message200.ALTITUDE_TYPE_AGL
        msg200.set_focus = 1
        msg200.focus_type = Message200.FOCUS_TYPE_MANUAL

        wrapper = MessageWrapper(MessageWrapper.MSGNULL)
        encoded_msg = wrapper.wrap_message(1, 200, msg200, False)

        asyncio.get_running_loop().call_soon(self._stanag_server.tx_data, encoded_msg)

    #############
    ## LRF Related
    def sendLrfCommand(self, cmd):
        if self._stanag_server is None: return

        msg201 = Message201(Message201.MSGNULL)
        msg201.time_stamp = 0x00
        msg201.vehicle_id = self._eo_node.getVehicleId()
        msg201.cucs_id = 0xA0
        msg201.station_number = 4
        msg201.addressed_sensor = Message201.ADDRESSED_SENSOR_PLSPECIFIC
        msg201.system_operating_mode = Message201.SYSTEM_OPERATING_MODE_ACTIVE
        msg201.set_eo_sensor_mode = Message201.EO_SENSOR_MODE_COLOR
        msg201.set_ir_polarity = Message201.IR_POLARITY_WHITE_HOT
        msg201.image_output = Message201.IMAGE_OUTPUT_BOTH
        msg201.set_eo_ir_pointing_mode = Message201.EO_IR_POINTING_MODE_TARGET_SLAVED
        msg201.fire_laser_pointer = Message201.LASER_POINTER_FIRE

        msg201.fire_laser_rangefinder = cmd
        msg201.select_lrf_first_last_pulse = Message201.SELECT_LRF_PULSE_LAST
        
        msg201.set_laser_designator_code = 1
        msg201.initiate_laser_designator = Message201.INIT_LASER_DESIGNATOR_FIRE
        msg201.preplan_mode = Message201.PREPLAN_MODE_OPERATE_IN_MANUAL
        
        wrapper = MessageWrapper(MessageWrapper.MSGNULL)
        encoded_msg = wrapper.wrap_message(1, 201, msg201, False)

        asyncio.get_running_loop().call_soon(self._stanag_server.tx_data, encoded_msg)

    def onEoLrfStatusReceived(self, msg):

        #msg may be for ptz status
        if msg.reported_range >= 0.0:

            lrf_state = "Off"
            
            if msg.fire_laser_rangefinder_status == Message302_fire_laser_rangefinder_status.ON_SAFED:
                lrf_state = "On-Safed"
            elif msg.fire_laser_rangefinder_status == Message302_fire_laser_rangefinder_status.ARMED:
                lrf_state = "Armed"
            elif msg.fire_laser_rangefinder_status == Message302_fire_laser_rangefinder_status.MASKED:
                lrf_state = "Masked"
            elif msg.fire_laser_rangefinder_status == Message302_fire_laser_rangefinder_status.RECHARGING:
                lrf_state = "Recharging"
            elif msg.fire_laser_rangefinder_status == Message302_fire_laser_rangefinder_status.FIRING:
                lrf_state = "Firing"
                self.lbl_lrf_range.setText("Range: {:.2f} m".format(msg.reported_range))
            else:
                self.lbl_lrf_range.setText("Range: 0.0")

            self.lbl_lrf_status.setText("State: {}".format(lrf_state))
        
        if msg.actual_horizontal_field_of_view != -1000.0:
            self._last_known_zoom = msg.actual_horizontal_field_of_view
            self.lbl_zoom_status.setText("{:.2f}".format(msg.actual_horizontal_field_of_view))

    #Mast related
    def onMastStatusReceived(self, msg):
        if msg.vehicle_id != self._eo_node.getVehicleId():
            return
        
        self.progressMastHeight.setMinimum(msg.min_height*10)
        #scale the values as step count for progress is 1
        self.progressMastHeight.setMaximum(msg.max_height*10)
        self.progressMastHeight.setProperty("value", msg.current_height*10)

        self.lbl_mast_height.setText("{:.1f} m".format(msg.current_height))

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
        msg20030.station_number = 2
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