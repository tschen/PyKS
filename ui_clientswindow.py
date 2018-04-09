#############################################################################
##
## Copyright (c) 2017 Tim Chen
##
## This file is part of PyKS.
##
## This file may be used under the terms of the GNU General Public License
## version 3.0 as published by the Free Software Foundation and appearing in
## the file LICENSE included in the packaging of this file.  Please review the
## following information to ensure the GNU General Public License version 3.0
## requirements will be met: http://www.gnu.org/copyleft/gpl.html.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
## See the GNU Public License along with PyKS.
##
#############################################################################
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'client_window.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ClientsWindow(object):
    def setupUi(self, ClientsWindow):
        ClientsWindow.setObjectName("ClientsWindow")
        ClientsWindow.resize(280, 466)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/clients.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ClientsWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(ClientsWindow)
        self.centralwidget.setMinimumSize(QtCore.QSize(280, 425))
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.clientsTableView = KeyPressTableView(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.clientsTableView.sizePolicy().hasHeightForWidth())
        self.clientsTableView.setSizePolicy(sizePolicy)
        self.clientsTableView.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.clientsTableView.setFont(font)
        self.clientsTableView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.clientsTableView.setAcceptDrops(False)
        self.clientsTableView.setDragEnabled(True)
        self.clientsTableView.setDragDropOverwriteMode(False)
        self.clientsTableView.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.clientsTableView.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.clientsTableView.setAlternatingRowColors(True)
        self.clientsTableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.clientsTableView.setShowGrid(False)
        self.clientsTableView.setSortingEnabled(True)
        self.clientsTableView.setObjectName("clientsTableView")
        self.clientsTableView.horizontalHeader().setMinimumSectionSize(100)
        self.clientsTableView.horizontalHeader().setStretchLastSection(False)
        self.verticalLayout.addWidget(self.clientsTableView)
        ClientsWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(ClientsWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 280, 21))
        self.menubar.setObjectName("menubar")
        ClientsWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(ClientsWindow)
        self.statusbar.setObjectName("statusbar")
        ClientsWindow.setStatusBar(self.statusbar)

        self.retranslateUi(ClientsWindow)
        QtCore.QMetaObject.connectSlotsByName(ClientsWindow)

    def retranslateUi(self, ClientsWindow):
        _translate = QtCore.QCoreApplication.translate
        ClientsWindow.setWindowTitle(_translate("ClientsWindow", "Clients"))
        self.label.setText(_translate("ClientsWindow", "Clients"))

from widgets import KeyPressTableView
import resources_rc
