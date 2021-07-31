import os
import sys
import logging

from PyQt5 import uic
from PyQt5.QtCore import Qt, QTimer, QDir, QSignalBlocker
from PyQt5.QtGui import QCloseEvent, QIcon, QTextBlock
from PyQt5.QtWidgets import (QApplication, QLabel, QCalendarWidget, QFrame, QTabWidget, QTreeView,
                             QTableWidget, QFileSystemModel, QPlainTextEdit, QToolBar, QWidget,
                             QWidgetAction, QComboBox, QAction, QSizePolicy, QInputDialog)

from PyQtAds import QtAds
from models.eo_station_node import EoStationNode
from models.vehicle_model import VehicleModel

from models.vehicle_node import VehicleNode

from widgets.c2_eo_station_widget import C2EoStationWidget
from stanag4586vsm.stanag_server import *

UI_FILE = os.path.join(os.path.dirname(__file__), 'templates/qt/mainwindow.ui')
MainWindowUI, MainWindowBase = uic.loadUiType(UI_FILE)

import demo_rc # pyrcc5 demo\demo.qrc -o examples\centralWidget\demo_rc.py

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT)

logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)


def svg_icon(filename: str):
    '''Helper function to create an SVG icon'''
    # This is a workaround, because because in item views SVG icons are not
    # properly scaled and look blurry or pixelate
    icon = QIcon(filename)
    icon.addPixmap(icon.pixmap(92))
    return icon
    

class MainWindow(MainWindowUI, MainWindowBase):

    __model_vehicles = None

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setupUi(self)
 
        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.OpaqueSplitterResize, True)
        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.XmlCompressionEnabled, False)
        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.FocusHighlighting, True)
        self.dock_manager = QtAds.CDockManager(self)
        
        txt_lbl = QLabel()
        txt_lbl.setText("Will be repalced by a map")
        # self._central_tab_widget.addTab(txt_lbl, "Map")

        central_dock_widget = QtAds.CDockWidget("CentralWidget")
        central_dock_widget.setWidget(txt_lbl)
        # central_dock_widget.setFeature(QtAds.DockWidgetArea)
        self._central_dock_area = self.dock_manager.setCentralWidget(central_dock_widget)

        #setup data
        self.__model_vehicles = VehicleModel(stanag_server, self.uiActionRequested)

        # create other dock widgets
        vehicles_tree = QTreeView()
        vehicles_tree.setFrameShape(QFrame.NoFrame)

        self.__model_vehicles.setOwingTreeWidget(vehicles_tree)
        vehicles_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        vehicles_tree.customContextMenuRequested.connect(self.__model_vehicles.contextMenuRequested)

        vehicles_tree.setModel(self.__model_vehicles)
        vehicle_explorer_dock_widget = QtAds.CDockWidget("Vehicle Explorer")
        vehicle_explorer_dock_widget.setWidget(vehicles_tree)
        vehicle_explorer_dock_widget.resize(150, 250)
        vehicle_explorer_dock_widget.setMinimumSize(100, 250)
        self.dock_manager.addDockWidget(QtAds.DockWidgetArea.LeftDockWidgetArea, vehicle_explorer_dock_widget, self._central_dock_area)
        self.menuView.addAction(vehicle_explorer_dock_widget.toggleViewAction())
        
        self.create_perspective_ui()
        
    def create_perspective_ui(self):
        save_perspective_action = QAction("Create Perspective", self)
        save_perspective_action.setIcon(svg_icon(":/adsdemo/images/picture_in_picture.svg"))
        save_perspective_action.triggered.connect(self.save_perspective)
        perspective_list_action = QWidgetAction(self)
        self.perspective_combobox = QComboBox(self)
        self.perspective_combobox.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.perspective_combobox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.perspective_combobox.activated[str].connect(self.dock_manager.openPerspective)
        perspective_list_action.setDefaultWidget(self.perspective_combobox)
        self.toolBar.addSeparator()
        self.toolBar.addAction(perspective_list_action)
        self.toolBar.addAction(save_perspective_action)
        
    def save_perspective(self):
        perspective_name, ok = QInputDialog.getText(self, "Save Perspective", "Enter Unique name:")
        if not ok or not perspective_name:
            return
        
        self.dock_manager.addPerspective(perspective_name)
        blocker = QSignalBlocker(self.perspective_combobox)
        self.perspective_combobox.clear()
        self.perspective_combobox.addItems(self.dock_manager.perspectiveNames())
        self.perspective_combobox.setCurrentText(perspective_name)
        
    def closeEvent(self, event: QCloseEvent):
        self.dock_manager.deleteLater()
        super().closeEvent(event)

    def tabCloseRequested(self, tab_id):
        if tab_id > 0:
            self._central_tab_widget.removeTab(tab_id)

    def openVideoWidget(self, requesting_node):

        dock_widget = QtAds.CDockWidget("Video Controls [v-{}:s-{}]".format(requesting_node.getVehicleId(), requesting_node.getStationId()))
        
        simple_widget = QWidget()
        vw = C2EoStationWidget(simple_widget, requesting_node, stanag_server)
        dock_widget.setWidget(simple_widget)

        self.dock_manager.addDockWidgetTabToArea(dock_widget, self._central_dock_area)

    def uiActionRequested(self, requesting_node):
        """Called by treeview nodes etc to open new windows"""
        if type(requesting_node) is EoStationNode:
            self.openVideoWidget(requesting_node)

stanag_server = None

async def setup_stanag_server():

    global stanag_server

    logger.debug("Creating server")
    stanag_server = StanagServer(logging.DEBUG)

    await stanag_server.setup_service(loop, StanagServer.MODE_CUCS)

    logger.info("STANAG iface active")

if __name__ == '__main__':
    import asyncio
    from qasync import QEventLoop

    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    # asyncio.wait(setup_stanag_server())
    loop.run_until_complete(setup_stanag_server())
    
    with loop:
        w = MainWindow()
        w.show()
        loop.run_forever()