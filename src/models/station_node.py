# based on https://gist.github.com/nbassler/342fc56c42df27239fa5276b79fca8e6

from .base_node import BaseNode


class StationNode(BaseNode):

    #Flags indicating whether this station is controlled/monitored
    __monitored = False
    __controlled = False
    
    def __init__(self, data):
        super().__init__(data)

    def isControlled(self):
        return self.__controlled

    def isMonitored(self):
        return self.__monitored

    def setMonitorAndControlled(self, monitored, controlled):
        if monitored is not None: self.__monitored = monitored
        if controlled is not None: self.__controlled = controlled