from PyQt5.QtWidgets import QAction, QMenu
from .base_node import BaseNode
from abc import ABC, abstractmethod
import logging
import os
class StationNode(BaseNode, ABC):

    #Flags indicating whether this station is controlled/monitored
    __monitored = False
    __controlled = False

    __action_req_ctrl = None
    __action_req_mon = None
    __action_req_dis_ctrl = None
    __action_req_dis_mon = None

    
    def __init__(self, data, vehicle_id, station_id, station_type, stanag_server):
        super().__init__(data, stanag_server)

        self._vehicle_id = vehicle_id
        self._station_id  = station_id
        self._station_type = station_type


        DEBUG_LEVEL = os.getenv("OPENC2_DEBUG_LEVEL")
        self._logger = logging.getLogger(type(self).__name__)
        
        if DEBUG_LEVEL is not None:
            self._logger.setLevel(int(DEBUG_LEVEL))
        else:
            self._logger.setLevel(logging.CRITICAL)

        StationNode.setupContextMenuActions(self)

    def setupContextMenuActions(self):
        self.__action_req_ctrl = QAction("Request Control")
        self.__action_req_mon = QAction("Request Monitor")
        self.__action_req_dis_ctrl = QAction("Release Control")
        self.__action_req_dis_mon = QAction("Release Monitor")

        self.__action_req_ctrl.triggered.connect(self.requestControl)
        self.__action_req_mon.triggered.connect(self.requestMonitor)
        self.__action_req_dis_ctrl.triggered.connect(self.requestDisconnectControl)
        self.__action_req_dis_mon.triggered.connect(self.requestDisconnectMonitor)


    def isControlled(self):
        return self.__controlled

    def isMonitored(self):
        return self.__monitored

    def setMonitorAndControlled(self, monitored, controlled):
        if monitored is not None: self.__monitored = monitored
        if controlled is not None: self.__controlled = controlled

    def getType(self):
        return self._station_type

    @abstractmethod
    def processConfigResponse(self, msg):
        """implementation to be provided by child classes"""

    def getContextMenuActions(self):
        """Returns node specific context menu"""

        #enable/disable actions
        if self.isControlled():
            self.__action_req_ctrl.setEnabled(False)
            self.__action_req_dis_ctrl.setEnabled(True)
        else:
            self.__action_req_ctrl.setEnabled(True)
            self.__action_req_dis_ctrl.setEnabled(False)

        if self.isMonitored():
            self.__action_req_mon.setEnabled(False)
            self.__action_req_dis_mon.setEnabled(True)
        else:
            self.__action_req_mon.setEnabled(True)
            self.__action_req_dis_mon.setEnabled(False)

        return [self.__action_req_ctrl, self.__action_req_mon, self.__action_req_dis_ctrl, self.__action_req_dis_mon]

    def requestMonitor(self, qa):
        self._logger.debug("requestMonitor")

        self._stanag_server.get_entity_controller().monitor_request(self._station_id, self._vehicle_id)

    def requestControl(self, qa):
        self._logger.debug("requestControl")

        self._stanag_server.get_entity_controller().control_request(self._station_id, self._vehicle_id)

    def requestDisconnectMonitor(self, qa):
        self._logger.debug("requestDisconnectMonitor")

        self._stanag_server.get_entity_controller().monitor_release(self._station_id, self._vehicle_id)

    def requestDisconnectControl(self, qa):
        self._logger.debug("requestDisconnectControl")

        self._stanag_server.get_entity_controller().control_release(self._station_id, self._vehicle_id)