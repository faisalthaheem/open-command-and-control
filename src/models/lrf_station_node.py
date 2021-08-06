# based on https://gist.github.com/nbassler/342fc56c42df27239fa5276b79fca8e6

from PyQt5.QtWidgets import QAction
from stanag4586edav1.message20020 import *

from .station_node import StationNode

class LrfStationNode(StationNode):

    def __init__(self, data, vehicle_id, station_id, station_type, stanag_server, cb_ui_action_request):
        super().__init__(data, vehicle_id, station_id, station_type, stanag_server, cb_ui_action_request)

        LrfStationNode.setupContextMenuActions(self)

    def setupContextMenuActions(self):
        self._action_open_lrf_controls = QAction("Open LRF Controls")
        self._action_open_lrf_controls.triggered.connect(self.openLrfControlsTriggerd)

    def processConfigResponse(self, msg):
        pass

    def getContextMenuActions(self):

        contextMenuActions = super().getContextMenuActions()

        if self.isControlled():
            self._action_open_lrf_controls.setEnabled(True)
        else:
            self._action_open_lrf_controls.setEnabled(False)

        contextMenuActions.append(self._action_open_lrf_controls)

        return contextMenuActions

    def openLrfControlsTriggerd(self, qa):
        self.raiseUiActionRequest()
