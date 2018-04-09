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

# Form implementation generated from reading ui file 'queue_window.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_QueueWindow(object):
    def setupUi(self, QueueWindow):
        QueueWindow.setObjectName("QueueWindow")
        QueueWindow.resize(343, 462)
        QueueWindow.setAcceptDrops(True)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/song_queue.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        QueueWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(QueueWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.queueTableView = KeyPressTableView(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.queueTableView.sizePolicy().hasHeightForWidth())
        self.queueTableView.setSizePolicy(sizePolicy)
        self.queueTableView.setMinimumSize(QtCore.QSize(325, 377))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.queueTableView.setFont(font)
        self.queueTableView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.queueTableView.setAcceptDrops(True)
        self.queueTableView.setDragEnabled(True)
        self.queueTableView.setDragDropOverwriteMode(False)
        self.queueTableView.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.queueTableView.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.queueTableView.setAlternatingRowColors(True)
        self.queueTableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.queueTableView.setShowGrid(False)
        self.queueTableView.setObjectName("queueTableView")
        self.verticalLayout.addWidget(self.queueTableView)
        QueueWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(QueueWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 343, 21))
        self.menubar.setObjectName("menubar")
        QueueWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(QueueWindow)
        self.statusbar.setObjectName("statusbar")
        QueueWindow.setStatusBar(self.statusbar)

        self.retranslateUi(QueueWindow)
        QtCore.QMetaObject.connectSlotsByName(QueueWindow)

    def retranslateUi(self, QueueWindow):
        _translate = QtCore.QCoreApplication.translate
        QueueWindow.setWindowTitle(_translate("QueueWindow", "Song Queue"))
        self.label_2.setText(_translate("QueueWindow", "Song Queue"))

from widgets import KeyPressTableView
import resources_rc
