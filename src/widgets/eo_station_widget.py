# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'templates/qt/eo_station_widget.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(776, 651)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.group_video = QtWidgets.QGroupBox(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.group_video.sizePolicy().hasHeightForWidth())
        self.group_video.setSizePolicy(sizePolicy)
        self.group_video.setObjectName("group_video")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.group_video)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.group_video_vertical_layout = QtWidgets.QVBoxLayout()
        self.group_video_vertical_layout.setSpacing(6)
        self.group_video_vertical_layout.setObjectName("group_video_vertical_layout")
        self.groupBox_3 = QtWidgets.QGroupBox(self.group_video)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_3.sizePolicy().hasHeightForWidth())
        self.groupBox_3.setSizePolicy(sizePolicy)
        self.groupBox_3.setObjectName("groupBox_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.btn_play = QtWidgets.QPushButton(self.groupBox_3)
        self.btn_play.setObjectName("btn_play")
        self.horizontalLayout_2.addWidget(self.btn_play)
        self.btn_stop = QtWidgets.QPushButton(self.groupBox_3)
        self.btn_stop.setObjectName("btn_stop")
        self.horizontalLayout_2.addWidget(self.btn_stop)
        self.group_video_vertical_layout.addWidget(self.groupBox_3)
        self.verticalLayout.addLayout(self.group_video_vertical_layout)
        self.horizontalLayout.addWidget(self.group_video)
        self.group_box_controls = QtWidgets.QGroupBox(Form)
        self.group_box_controls.setObjectName("group_box_controls")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.group_box_controls)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.btnUp = QtWidgets.QPushButton(self.group_box_controls)
        self.btnUp.setObjectName("btnUp")
        self.verticalLayout_3.addWidget(self.btnUp)
        self.widget = QtWidgets.QWidget(self.group_box_controls)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setObjectName("widget")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.btnLeft = QtWidgets.QPushButton(self.widget)
        self.btnLeft.setObjectName("btnLeft")
        self.horizontalLayout_3.addWidget(self.btnLeft)
        self.btnRight = QtWidgets.QPushButton(self.widget)
        self.btnRight.setObjectName("btnRight")
        self.horizontalLayout_3.addWidget(self.btnRight)
        self.verticalLayout_3.addWidget(self.widget)
        self.btnDown = QtWidgets.QPushButton(self.group_box_controls)
        self.btnDown.setObjectName("btnDown")
        self.verticalLayout_3.addWidget(self.btnDown)
        self.verticalLayout_2.addLayout(self.verticalLayout_3)
        self.groupBox = QtWidgets.QGroupBox(self.group_box_controls)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.btnMastUp = QtWidgets.QPushButton(self.groupBox)
        self.btnMastUp.setObjectName("btnMastUp")
        self.horizontalLayout_4.addWidget(self.btnMastUp)
        self.btnMastDown = QtWidgets.QPushButton(self.groupBox)
        self.btnMastDown.setObjectName("btnMastDown")
        self.horizontalLayout_4.addWidget(self.btnMastDown)
        self.verticalLayout_4.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.progressMastHeight = QtWidgets.QProgressBar(self.groupBox)
        self.progressMastHeight.setMinimum(1)
        self.progressMastHeight.setMaximum(10)
        self.progressMastHeight.setProperty("value", 1)
        self.progressMastHeight.setOrientation(QtCore.Qt.Vertical)
        self.progressMastHeight.setObjectName("progressMastHeight")
        self.horizontalLayout_5.addWidget(self.progressMastHeight)
        self.sliderMastHeight = QtWidgets.QSlider(self.groupBox)
        self.sliderMastHeight.setMinimum(1)
        self.sliderMastHeight.setMaximum(10)
        self.sliderMastHeight.setOrientation(QtCore.Qt.Vertical)
        self.sliderMastHeight.setInvertedControls(False)
        self.sliderMastHeight.setObjectName("sliderMastHeight")
        self.horizontalLayout_5.addWidget(self.sliderMastHeight)
        self.verticalLayout_4.addLayout(self.horizontalLayout_5)
        self.groupBox_2 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.lbl_lrf_status = QtWidgets.QLabel(self.groupBox_2)
        self.lbl_lrf_status.setObjectName("lbl_lrf_status")
        self.verticalLayout_5.addWidget(self.lbl_lrf_status)
        self.lbl_lrf_range = QtWidgets.QLabel(self.groupBox_2)
        self.lbl_lrf_range.setObjectName("lbl_lrf_range")
        self.verticalLayout_5.addWidget(self.lbl_lrf_range)
        self.cmd_lrf_off = QtWidgets.QPushButton(self.groupBox_2)
        self.cmd_lrf_off.setObjectName("cmd_lrf_off")
        self.verticalLayout_5.addWidget(self.cmd_lrf_off)
        self.cmd_lrf_on = QtWidgets.QPushButton(self.groupBox_2)
        self.cmd_lrf_on.setObjectName("cmd_lrf_on")
        self.verticalLayout_5.addWidget(self.cmd_lrf_on)
        self.cmd_lrf_arm = QtWidgets.QPushButton(self.groupBox_2)
        self.cmd_lrf_arm.setObjectName("cmd_lrf_arm")
        self.verticalLayout_5.addWidget(self.cmd_lrf_arm)
        self.cmd_lrf_fire = QtWidgets.QPushButton(self.groupBox_2)
        self.cmd_lrf_fire.setObjectName("cmd_lrf_fire")
        self.verticalLayout_5.addWidget(self.cmd_lrf_fire)
        self.verticalLayout_4.addWidget(self.groupBox_2)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.horizontalLayout.addWidget(self.group_box_controls)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.group_video.setTitle(_translate("Form", "Live Video"))
        self.groupBox_3.setTitle(_translate("Form", "Video playback controls"))
        self.btn_play.setText(_translate("Form", "Play"))
        self.btn_stop.setText(_translate("Form", "Stop"))
        self.group_box_controls.setTitle(_translate("Form", "Controls"))
        self.btnUp.setText(_translate("Form", "Up"))
        self.btnLeft.setText(_translate("Form", "<"))
        self.btnRight.setText(_translate("Form", ">"))
        self.btnDown.setText(_translate("Form", "Down"))
        self.groupBox.setTitle(_translate("Form", "Mast Controls"))
        self.btnMastUp.setText(_translate("Form", "Up"))
        self.btnMastDown.setText(_translate("Form", "Down"))
        self.groupBox_2.setTitle(_translate("Form", "LRF Controls"))
        self.lbl_lrf_status.setText(_translate("Form", "State: Off"))
        self.lbl_lrf_range.setText(_translate("Form", "Range: 0.0m"))
        self.cmd_lrf_off.setText(_translate("Form", "Power Off"))
        self.cmd_lrf_on.setText(_translate("Form", "Power On"))
        self.cmd_lrf_arm.setText(_translate("Form", "Arm"))
        self.cmd_lrf_fire.setText(_translate("Form", "Fire"))
