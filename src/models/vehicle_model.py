# based on https://gist.github.com/nbassler/342fc56c42df27239fa5276b79fca8e6

from PyQt5 import QtCore
from .vehicle_node import VehicleNode
import logging

from stanag4586vsm.stanag_server import *


class VehicleModel(QtCore.QAbstractItemModel):

    __root_node = None
    __root_node_ugv = None
    __root_node_uav = None
    __root_node_usv = None
    __root_node_uuv = None
    __stanag_server = None

    def __init__(self, stanag_server, nodes = None):
        
        self.__logger = logging.getLogger("VehicleModel")
        self.__logger.setLevel(logging.DEBUG)

        QtCore.QAbstractItemModel.__init__(self)
        self._root = VehicleNode(None)
        self.__root_node_ugv = VehicleNode(("UGVs","Ground vehicles"))
        self.__root_node_uav = VehicleNode(("UAVs","Air vehicles"))
        self.__root_node_usv = VehicleNode(("USVs","Sea vehicles"))
        self.__root_node_uuv = VehicleNode(("UUVs","Submerged vehicles"))

        self._root.addChild(self.__root_node_ugv)
        self._root.addChild(self.__root_node_uav)
        self._root.addChild(self.__root_node_usv)
        self._root.addChild(self.__root_node_uuv)

        if nodes is not None:
            for node in nodes:
                self._root.addChild(node)


        #instantiate stanag server and bind to events
        self.__stanag_server = stanag_server
        self.__stanag_server.get_entity_controller().set_callback_for_vehicle_discovery(self.handle_vehicle_discovery)


    def rowCount(self, index):
        if index.isValid():
            return index.internalPointer().childCount()
        return self._root.childCount()

    def addChild(self, node, _parent):
        if not _parent or not _parent.isValid():
            parent = self._root
        else:
            parent = _parent.internalPointer()
        parent.addChild(node)

    def index(self, row, column, _parent=None):
        if not _parent or not _parent.isValid():
            parent = self._root
        else:
            parent = _parent.internalPointer()

        if not QtCore.QAbstractItemModel.hasIndex(self, row, column, _parent):
            return QtCore.QModelIndex()

        child = parent.child(row)
        if child:
            return QtCore.QAbstractItemModel.createIndex(self, row, column, child)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if index.isValid():
            p = index.internalPointer().parent()
            if p:
                return QtCore.QAbstractItemModel.createIndex(self, p.row(), 0, p)
        return QtCore.QModelIndex()

    def columnCount(self, index):
        if index.isValid():
            return index.internalPointer().columnCount()
        return self._root.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return node.data(index.column())
        return None
    
    def handle_vehicle_discovery(self, controller, vehicles):
        self.__logger.info("Vehicles discovered [{}]".format(vehicles))

        discovered_vehicles = vehicles

        #for poc purposes we have just one vehicle
        #we check if it's not already controlled by us, then we request for it to be controlled
        for veh_id in discovered_vehicles.keys():
            if discovered_vehicles[veh_id][EntityController.KEY_CONTROLLED] is False:
                controller.control_request(0x0, veh_id)
