# based on https://gist.github.com/nbassler/342fc56c42df27239fa5276b79fca8e6

from .station_node import StationNode
class EoStationNode(StationNode):
    def __init__(self, data):
        super().__init__(data)