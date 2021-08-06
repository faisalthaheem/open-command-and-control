from PyQt5.QtWidgets import QAction
from .station_node import StationNode
from .eo_station_node import EoStationNode
from .mast_station_node import MastStationNode
from .lrf_station_node import LrfStationNode

from stanag4586vsm.entity_controller import EntityController
from stanag4586edav1.message300 import Message300
from stanag4586edav1.message20010 import *

class VehicleNode(StationNode):
    
    __eo_payaload_types = [
        Message300.PAYLOAD_TYPE_EO, 
        Message300.PAYLOAD_TYPE_EOIR, 
        Message300.PAYLOAD_TYPE_IR,
        Message300.PAYLOAD_TYPE_FIXED_CAMERA,
    ]

    def __init__(self, data, vehicle_id, station_id, station_type, stanag_server, cb_ui_action_request):
        super().__init__(data, vehicle_id, station_id, station_type, stanag_server, cb_ui_action_request)

        self.setupContextMenuActions()

    def setupContextMenuActions(self):
        self._action_open_drive_controls = QAction("Open Drive Controls")
        self._action_open_drive_controls.triggered.connect(self.open_drive_controls_triggered)

    def sync_stations(self, stations):

        for station_id in stations.keys():
            self.__sync_station(station_id, stations[station_id])

    def __sync_station(self, station_id, station_data):
        
        station = self.hasChild(station_id)
        if station is None:
            station = self.__new_station_node(station_id, station_data)

        if station is None:
            self._logger.warn("Unable to process station [{}]".format(station_id))
        else:
            #otherwise update control/monitor of this station
            station.setMonitorAndControlled(
                station_data[EntityController.KEY_MONITORED],
                station_data[EntityController.KEY_CONTROLLED],
            )

            if station.getType() in self.__eo_payaload_types:
                vehicle_id = self.data(0)
                station_id = station.data(0)

                self._stanag_server.get_entity_controller().query_request(vehicle_id, station_id, Message20010.QUERY_TYPE_SEND_CONFIG)

            

    def __new_station_node(self, station_id, station_data):
        
        station = None
        
        if station_data[EntityController.KEY_TYPE] in self.__eo_payaload_types:
            station = EoStationNode(
                (station_id, "EO"),
                self._vehicle_id,
                station_id, 
                station_data[EntityController.KEY_TYPE],
                self._stanag_server,
                self._cb_ui_action_request)
        
        elif station_data[EntityController.KEY_TYPE] == Message300.PAYLOAD_TYPE_MAST:
            station = MastStationNode(
                (station_id, "Mast"),
                self._vehicle_id,
                station_id, 
                station_data[EntityController.KEY_TYPE],
                self._stanag_server,
                self._cb_ui_action_request)
            
        elif station_data[EntityController.KEY_TYPE] == Message300.PAYLOAD_TYPE_LRF:
            station = MastStationNode(
                (station_id, "Lrf"),
                self._vehicle_id,
                station_id, 
                station_data[EntityController.KEY_TYPE],
                self._stanag_server,
                self._cb_ui_action_request)
        
        if station is not None:
            self.addChild(station)

        return station

    def processConfigResponse(self, msg):
        pass

    def open_drive_controls_triggered(self):
        self._logger.debug("Drive controls not implemented")

    def getContextMenuActions(self):

        contextMenuActions = super().getContextMenuActions()

        if self.isControlled():
            self._action_open_drive_controls.setEnabled(True)
        else:
            self._action_open_drive_controls.setEnabled(False)
        
        contextMenuActions.append(self._action_open_drive_controls)

        return contextMenuActions
