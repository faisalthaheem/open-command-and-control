import os
import sys
import logging

from PyQt5 import uic
from PyQt5.QtCore import Qt, QTimer, QDir, QSignalBlocker
from PyQt5.QtGui import QCloseEvent, QIcon
from PyQt5.QtWidgets import (QApplication, QLabel, QCalendarWidget, QFrame, QTreeView,
                             QTableWidget, QFileSystemModel, QPlainTextEdit, QToolBar,
                             QWidgetAction, QComboBox, QAction, QSizePolicy, QInputDialog)

from PyQtAds import QtAds
from models.vehicle_model import VehicleModel

from models.vehicle_node import VehicleNode

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
        
        # Set central widget
        text_edit = QPlainTextEdit()
        text_edit.setPlaceholderText("This is the central editor. Enter your text here.")
        central_dock_widget = QtAds.CDockWidget("CentralWidget")
        central_dock_widget.setWidget(text_edit)
        central_dock_area = self.dock_manager.setCentralWidget(central_dock_widget)
        central_dock_area.setAllowedAreas(QtAds.DockWidgetArea.OuterDockAreas)
        
        #setup data
        self.__model_vehicles = VehicleModel(stanag_server)

        # create other dock widgets
        vehicles_tree = QTreeView()
        vehicles_tree.setFrameShape(QFrame.NoFrame)

        self.__model_vehicles.setOwingTreeWidget(vehicles_tree)
        vehicles_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        vehicles_tree.customContextMenuRequested.connect(self.__model_vehicles.contextMenuRequested)

        vehicles_tree.setModel(self.__model_vehicles)
        data_dock_widget = QtAds.CDockWidget("File system")
        data_dock_widget.setWidget(vehicles_tree)
        data_dock_widget.resize(150, 250)
        data_dock_widget.setMinimumSize(100, 250)
        file_area = self.dock_manager.addDockWidget(QtAds.DockWidgetArea.LeftDockWidgetArea, data_dock_widget, central_dock_area)
        self.menuView.addAction(data_dock_widget.toggleViewAction())
        
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