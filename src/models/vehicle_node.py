from .station_node import StationNode
from .eo_station_node import EoStationNode

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
    
    def __init__(self, data, station_type, stanag_server):
        super().__init__(data, station_type, stanag_server)

    def sync_stations(self, stations):

        for station_id in stations.keys():
            self.__sync_station(station_id, stations[station_id])

    def __sync_station(self, station_id, station_data):
        
        station = self.hasChild(station_id)
        if station is None:
            station = self.__new_station_node(station_id, station_data)
            self.addChild(station)

        if station is not None:
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
        
        if station_data[EntityController.KEY_TYPE] in self.__eo_payaload_types:
            return EoStationNode((station_id, "EO"), station_data[EntityController.KEY_TYPE], self._stanag_server)

    def processConfigResponse(self, msg):
        pass    