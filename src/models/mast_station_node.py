# based on https://gist.github.com/nbassler/342fc56c42df27239fa5276b79fca8e6

from PyQt5.QtWidgets import QAction
from stanag4586edav1.message20020 import *

from .station_node import StationNode

class MastStationNode(StationNode):

    def __init__(self, data, vehicle_id, station_id, station_type, stanag_server, cb_ui_action_request):
        super().__init__(data, vehicle_id, station_id, station_type, stanag_server, cb_ui_action_request)

        MastStationNode.setupContextMenuActions(self)

    def setupContextMenuActions(self):
        self._action_open_mast_controls = QAction("Open Mast Controls")
        self._action_open_mast_controls.triggered.connect(self.openMastControlsTriggerd)

    def processConfigResponse(self, msg):
        pass

    def getContextMenuActions(self):

        contextMenuActions = super().getContextMenuActions()

        if self.isControlled():
            self._action_open_mast_controls.setEnabled(True)
        else:
            self._action_open_mast_controls.setEnabled(False)

        contextMenuActions.append(self._action_open_mast_controls)

        return contextMenuActions

    def openMastControlsTriggerd(self, qa):
        self.raiseUiActionRequest()
