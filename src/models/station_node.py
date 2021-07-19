from .base_node import BaseNode
from abc import ABC, abstractmethod
import logging
import os
class StationNode(BaseNode, ABC):

    #Flags indicating whether this station is controlled/monitored
    __monitored = False
    __controlled = False
    
    def __init__(self, data, station_type, stanag_server):
        super().__init__(data, stanag_server)
        self._station_type = station_type


        DEBUG_LEVEL = os.getenv("OPENC2_DEBUG_LEVEL")
        self._logger = logging.getLogger(type(self).__name__)
        
        if DEBUG_LEVEL is not None:
            self._logger.setLevel(int(DEBUG_LEVEL))
        else:
            self._logger.setLevel(logging.CRITICAL)

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
    def getContextMenuText(self):
        """Returns text used by treeview to show context menu action"""

    @abstractmethod
    def handleContextMenu(self):
        """Invoked by tree model when the node has been selected and corresponding menu item clicked"""

    @abstractmethod
    def processConfigResponse(self, msg):
        """implementation to be provided by child classes"""

    