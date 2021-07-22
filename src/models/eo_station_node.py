# based on https://gist.github.com/nbassler/342fc56c42df27239fa5276b79fca8e6

from PyQt5.QtWidgets import QAction
from stanag4586edav1.message20020 import *

from .station_node import StationNode

import json
class EoStationNode(StationNode):

    _daytime_rtsp_uri = ""

    def __init__(self, data, vehicle_id, station_id, station_type, stanag_server, cb_ui_action_request):
        super().__init__(data, vehicle_id, station_id, station_type, stanag_server, cb_ui_action_request)

        EoStationNode.setupContextMenuActions(self)

    def setupContextMenuActions(self):
        self._action_open_camera_controls = QAction("Open Camera Controls")
        self._action_open_camera_controls.triggered.connect(self.openCameraControlsTriggerd)

    def processConfigResponse(self, msg):
        self._logger.debug("Got config response [{}]".format(msg.get_response()))
        res = json.loads(msg.get_response())

        if res is not None:
            self._daytime_rtsp_uri = res["daylight"]

    def getMediaUri(self):
        return self._daytime_rtsp_uri

    def getContextMenuActions(self):

        contextMenuActions = super().getContextMenuActions()

        if self.isControlled():
            self._action_open_camera_controls.setEnabled(True)
        else:
            self._action_open_camera_controls.setEnabled(False)

        contextMenuActions.append(self._action_open_camera_controls)

        return contextMenuActions

    def openCameraControlsTriggerd(self, qa):
        self._logger.debug("Camera controls not implemented")
        self.raiseUiActionRequest()
