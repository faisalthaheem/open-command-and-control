# based on https://gist.github.com/nbassler/342fc56c42df27239fa5276b79fca8e6

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtGui import QColor, QCursor, QIcon
from PyQt5.QtWidgets import QAction, QMenu
from models.base_node import BaseNode
from models.eo_station_node import EoStationNode
from models.lrf_station_node import LrfStationNode
from models.mast_station_node import MastStationNode
from models.station_node import StationNode
from .vehicle_node import VehicleNode
import logging

from PyQt5.QtCore import pyqtSignal

from stanag4586edav1.message21 import Message21
from stanag4586edav1.message20040 import Message20040
from stanag4586vsm.stanag_server import *
from stanag4586edav1.message302 import *

class VehicleModel(QtCore.QAbstractItemModel):

    #recognized nodes
    _recognized_node_types = [LrfStationNode ,MastStationNode, VehicleNode, EoStationNode]

    #Public members
    onMastStatusReceived = pyqtSignal(Message20040)
    onEoLrfStatusReceived = pyqtSignal(Message302)
    
    #Private members
    __root_node = None
    __root_node_ugv = None
    __root_node_uav = None
    __root_node_usv = None
    __root_node_uuv = None
    __stanag_server = None

    """A callback which allows nodes to request the host app to open new dialogs"""
    """Signature is func(requesting_node)"""
    _cb_ui_action_request = None

    def __init__(self, stanag_server, cb_ui_action_request, nodes = None):
        
        self.__logger = logging.getLogger("VehicleModel")
        self.__logger.setLevel(logging.CRITICAL)

        self._cb_ui_action_request = cb_ui_action_request

        QtCore.QAbstractItemModel.__init__(self)
        self.__root_node = BaseNode(None, self.__stanag_server, cb_ui_action_request)
        self.__root_node_ugv = BaseNode(("UGVs","Ground vehicles"), self.__stanag_server, cb_ui_action_request)
        self.__root_node_uav = BaseNode(("UAVs","Air vehicles"), self.__stanag_server, cb_ui_action_request)
        self.__root_node_usv = BaseNode(("USVs","Sea vehicles"), self.__stanag_server, cb_ui_action_request)
        self.__root_node_uuv = BaseNode(("UUVs","Submerged vehicles"), self.__stanag_server, cb_ui_action_request)

        self.__root_node.addChild(self.__root_node_ugv)
        self.__root_node.addChild(self.__root_node_uav)
        self.__root_node.addChild(self.__root_node_usv)
        self.__root_node.addChild(self.__root_node_uuv)

        self._color_monitored = QColor.fromRgb(255,255,0)
        self._color_controlled = QColor.fromRgb(0,255,0)

        if nodes is not None:
            for node in nodes:
                self.__root_node.addChild(node)


        #instantiate stanag server and bind to events
        self.__stanag_server = stanag_server
        self.__stanag_server.get_entity_controller().set_callback_for_vehicle_discovery(self.handle_vehicle_discovery)
        self.__stanag_server.get_entity_controller().set_callback_for_unhandled_messages(self.process_unhandled_message)


    def rowCount(self, index):
        if index.isValid():
            return index.internalPointer().childCount()
        return self.__root_node.childCount()

    def addChild(self, node, _parent):
        if not _parent or not _parent.isValid():
            parent = self.__root_node
        else:
            parent = _parent.internalPointer()
        parent.addChild(node)

    def index(self, row, column, _parent=None):
        if not _parent or not _parent.isValid():
            parent = self.__root_node
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
        return self.__root_node.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:

            if type(node) not in self._recognized_node_types:
                return node.data(index.column())

            if index.column() > 0:
                return node.data(index.column())
            else:
                text = node.data(index.column())                
                return text

        # if (role==QtCore.Qt.BackgroundColorRole) and (type(node) in [VehicleNode, EoStationNode]):
        #     if node.isControlled():
        #         return QtGui.QBrush(QtCore.Qt.green)
        #     elif node.isMonitored():
        #         return QtGui.QBrush(QtCore.Qt.yellow)

        if index.column() == 0 and (role==QtCore.Qt.DecorationRole) and (type(node) in self._recognized_node_types):
            if node.isControlled():
                return self._color_controlled
            elif node.isMonitored():
                return self._color_monitored
            else:
                return None

        return None

    def process_unhandled_message(self, wrapper, msg):
        
        if wrapper.message_type == 20020:
            """Config response message"""
            self.__logger.debug("Got config response ")

            vehicle = self.findVehicle(msg.vehicle_id)

            if vehicle is None:
                self.__logger.warn("Got config response for a vehicle [{}] that does not exist.".format(msg.vehicle_id))
                return

            station = vehicle.hasChild(msg.station_number)
            if station is None:
                self.__logger.warn("Got config response for a station [{}] for vehicle [{}] that does not exist.".format(msg.station_number, msg.vehicle_id))
                return

            station.processConfigResponse(msg)

        elif wrapper.message_type == 20040:
            self.__logger.debug("Got Mast status ")
            self.onMastStatusReceived.emit(msg)

        elif wrapper.message_type == 302:
            self.__logger.debug("Got EO/LRF status ")
            self.onEoLrfStatusReceived.emit(msg)


    
    def findVehicle(self, vehicle_id):
        """Looks up the vehicle by id in UGV, UAV, USV OR UUV root nodes
        Returns vehicleNode if found or None otherwise"""

        for root in [self.__root_node_ugv, self.__root_node_uav, self.__root_node_usv, self.__root_node_uuv]:
            v = root.hasChild(vehicle_id)
            if v is not None: return v

        return None

    def handle_vehicle_discovery(self, controller, vehicles):
        self.__logger.info("Vehicles discovered [{}]".format(vehicles))

        discovered_vehicles = vehicles

        #for poc purposes we have just one vehicle
        #we check if it's not already controlled by us, then we request for it to be controlled
        for veh_id in discovered_vehicles.keys():
            
            # temporary - send control request to the vehicle, will remove once context menus are introduced
            # if discovered_vehicles[veh_id][EntityController.KEY_CONTROLLED] is False:
            #     controller.control_request(0x0, veh_id)

            if discovered_vehicles[veh_id][EntityController.KEY_TYPE] == Message21.VEHICLE_TYPE_UGV:
                
                ugv = self.__root_node_ugv.hasChild(veh_id)
                if None == ugv:
                    self.__logger.debug("New ugv discovered [{}]".format(veh_id))
                    
                    if EntityController.KEY_META not in discovered_vehicles[veh_id].keys():
                        continue
                    if discovered_vehicles[veh_id][EntityController.KEY_META] is None or \
                       EntityController.KEY_CALL_SIGN not in discovered_vehicles[veh_id][EntityController.KEY_META].keys():
                        continue

                    call_sign = discovered_vehicles[veh_id][EntityController.KEY_META][EntityController.KEY_CALL_SIGN]
                    
                    ugv = VehicleNode((veh_id, call_sign), veh_id, 0, 0, self.__stanag_server, self._cb_ui_action_request)
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
        
        if type(node) in [LrfStationNode, MastStationNode ,EoStationNode, VehicleNode]:
            self.__logger.debug("Station node clicked")

            #nodeContext
            nodeActions = node.getContextMenuActions()

            ctxMenu = QMenu()
            for action in nodeActions:
                ctxMenu.addAction(action)

            # self.__cntx_menu.exec_(QCursor.pos())
            ctxMenu.exec_(QCursor.pos())

    def getSelectedNode(self):            
        if self.__owing_tree is None:
            return None

        selected_indexes = self.__owing_tree.selectedIndexes()
        if len(selected_indexes) > 0:
            node = selected_indexes[0].internalPointer()

            return node

        return None

    

    def nodeSpecificActionRequested(self, qa):
        
        node = self.getSelectedNode()
        if node is None: return
        
        if type(node) in [EoStationNode, VehicleNode]:
            node.handleContextMenu()