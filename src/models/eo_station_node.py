# based on https://gist.github.com/nbassler/342fc56c42df27239fa5276b79fca8e6

from stanag4586edav1.message20020 import *

from .station_node import StationNode
class EoStationNode(StationNode):
    def __init__(self, data, station_type, stanag_server):
        super().__init__(data, station_type, stanag_server)

    def processConfigResponse(self, msg):
        self._logger.debug("Got config response [{}]".format(msg.get_response()))