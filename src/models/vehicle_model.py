# based on https://gist.github.com/nbassler/342fc56c42df27239fa5276b79fca8e6

from PyQt5 import QtCore
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QAction, QMenu
from stanag4586edav1.message21 import Message21
from models.base_node import BaseNode

from models.eo_station_node import EoStationNode
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

    __cntx_menu = None
    __action_req_ctrl = None
    __action_req_mon = None
    __action_req_dis_ctrl = None
    __action_req_dis_mon = None

    def __init__(self, stanag_server, nodes = None):
        
        self.__logger = logging.getLogger("VehicleModel")
        self.__logger.setLevel(logging.DEBUG)

        QtCore.QAbstractItemModel.__init__(self)
        self._root = BaseNode(None)
        self.__root_node_ugv = BaseNode(("UGVs","Ground vehicles"))
        self.__root_node_uav = BaseNode(("UAVs","Air vehicles"))
        self.__root_node_usv = BaseNode(("USVs","Sea vehicles"))
        self.__root_node_uuv = BaseNode(("UUVs","Submerged vehicles"))

        self._root.addChild(self.__root_node_ugv)
        self._root.addChild(self.__root_node_uav)
        self._root.addChild(self.__root_node_usv)
        self._root.addChild(self.__root_node_uuv)

        if nodes is not None:
            for node in nodes:
                self._root.addChild(node)

        self.setupContextMenu()


        #instantiate stanag server and bind to events
        self.__stanag_server = stanag_server
        self.__stanag_server.get_entity_controller().set_callback_for_vehicle_discovery(self.handle_vehicle_discovery)

    def setupContextMenu(self):
        
        self.__action_req_ctrl = QAction("Request Control", self)
        self.__action_req_mon = QAction("Request Monitor", self)
        self.__action_req_dis_ctrl = QAction("Disonnect Control", self)
        self.__action_req_dis_mon = QAction("Disconnect Monitor", self)

        self.__action_req_ctrl.triggered.connect(self.requestControl)
        self.__action_req_mon.triggered.connect(self.requestMonitor)
        self.__action_req_dis_ctrl.triggered.connect(self.requestDisconnectControl)
        self.__action_req_dis_mon.triggered.connect(self.requestDisconnectMonitor)


        self.__cntx_menu = QMenu()
        self.__cntx_menu.addAction(self.__action_req_ctrl)
        self.__cntx_menu.addAction(self.__action_req_mon)
        self.__cntx_menu.addAction(self.__action_req_dis_ctrl)
        self.__cntx_menu.addAction(self.__action_req_dis_mon)

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
            
            # temporary - send control request to the vehicle, will remove once context menus are introduced
            if discovered_vehicles[veh_id][EntityController.KEY_CONTROLLED] is False:
                controller.control_request(0x0, veh_id)

            if discovered_vehicles[veh_id][EntityController.KEY_TYPE] == Message21.VEHICLE_TYPE_UGV:
                
                ugv = self.__root_node_ugv.hasChild(veh_id)
                if None == ugv:
                    self.__logger.debug("New ugv discovered [{}]".format(veh_id))
                    
                    call_sign = discovered_vehicles[veh_id][EntityController.KEY_META][EntityController.KEY_CALL_SIGN]
                    
                    ugv = VehicleNode((veh_id, call_sign))
                    self.__root_node_ugv.addChild(ugv)

                if None != ugv:
                    # Sync stations as ugv's children
                    ugv.sync_stations(discovered_vehicles[veh_id][EntityController.KEY_STATIONS])

                    #update monitor/control status
                    ugv.setMonitorAndControlled(
                        discovered_vehicles[veh_id][EntityController.KEY_MONITORED],
                        discovered_vehicles[veh_id][EntityController.KEY_CONTROLLED],
                    )

        self.layoutChanged.emit()

    def setOwingTreeWidget(self, tree):
        self.__owing_tree = tree

    def contextMenuRequested(self, pos):

        node = self.getSelectedNode()
        if node is None: return
        
        if type(node) == EoStationNode or type(node) == VehicleNode:
            self.__logger.debug("Station node clicked")
            self.__cntx_menu.exec_(QCursor.pos())

    def getSelectedNode(self):            
        if self.__owing_tree is None:
            return None

        selected_indexes = self.__owing_tree.selectedIndexes()
        if len(selected_indexes) > 0:
            node = selected_indexes[0].internalPointer()

            return node

        return None

    def requestMonitor(self, qa):
        self.__logger.debug("requestMonitor")
        
        node = self.getSelectedNode()
        if node is None: return

        # if type(node) == EoStationNode:
        #     self.startTimer

    def requestControl(self, qa):
        self.__logger.debug("requestControl")

    def requestDisconnectMonitor(self, qa):
        self.__logger.debug("requestDisconnectMonitor")

    def requestDisconnectControl(self, qa):
        self.__logger.debug("requestDisconnectControl")