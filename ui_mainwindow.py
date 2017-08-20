# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(873, 552)
        MainWindow.setFocusPolicy(QtCore.Qt.StrongFocus)
        MainWindow.setAnimated(True)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setText("")
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.SearchLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.SearchLabel.setFont(font)
        self.SearchLabel.setObjectName("SearchLabel")
        self.horizontalLayout.addWidget(self.SearchLabel)
        self.searchLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.searchLineEdit.setFont(font)
        self.searchLineEdit.setObjectName("searchLineEdit")
        self.horizontalLayout.addWidget(self.searchLineEdit)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.searchResultsTableView = QtWidgets.QTableView(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.searchResultsTableView.setFont(font)
        self.searchResultsTableView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.searchResultsTableView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.searchResultsTableView.setAlternatingRowColors(True)
        self.searchResultsTableView.setShowGrid(False)
        self.searchResultsTableView.setSortingEnabled(True)
        self.searchResultsTableView.setObjectName("searchResultsTableView")
        self.verticalLayout.addWidget(self.searchResultsTableView)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 873, 21))
        self.menubar.setObjectName("menubar")
        self.menu_File = QtWidgets.QMenu(self.menubar)
        self.menu_File.setObjectName("menu_File")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.dockWidget = QtWidgets.QDockWidget(MainWindow)
        self.dockWidget.setMinimumSize(QtCore.QSize(300, 477))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        self.dockWidget.setFont(font)
        self.dockWidget.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.dockWidget.setAcceptDrops(True)
        self.dockWidget.setFloating(False)
        self.dockWidget.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable|QtWidgets.QDockWidget.DockWidgetMovable)
        self.dockWidget.setWindowTitle("")
        self.dockWidget.setObjectName("dockWidget")
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_2.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.dockWidgetContents)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.playlistTableView = PlaylistTableView(self.dockWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.playlistTableView.sizePolicy().hasHeightForWidth())
        self.playlistTableView.setSizePolicy(sizePolicy)
        self.playlistTableView.setMinimumSize(QtCore.QSize(280, 377))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(11)
        self.playlistTableView.setFont(font)
        self.playlistTableView.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.playlistTableView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.playlistTableView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.playlistTableView.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.playlistTableView.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.playlistTableView.setDefaultDropAction(QtCore.Qt.CopyAction)
        self.playlistTableView.setAlternatingRowColors(True)
        self.playlistTableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.playlistTableView.setShowGrid(False)
        self.playlistTableView.setObjectName("playlistTableView")
        self.verticalLayout_2.addWidget(self.playlistTableView)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.playButton = QtWidgets.QPushButton(self.dockWidgetContents)
        self.playButton.setToolTipDuration(-1)
        self.playButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.playButton.setIcon(icon)
        self.playButton.setCheckable(False)
        self.playButton.setChecked(False)
        self.playButton.setAutoRepeat(False)
        self.playButton.setAutoDefault(False)
        self.playButton.setObjectName("playButton")
        self.horizontalLayout_2.addWidget(self.playButton)
        self.stopButton = QtWidgets.QPushButton(self.dockWidgetContents)
        self.stopButton.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("images/stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.stopButton.setIcon(icon1)
        self.stopButton.setAutoDefault(True)
        self.stopButton.setObjectName("stopButton")
        self.horizontalLayout_2.addWidget(self.stopButton)
        self.nextButton = QtWidgets.QPushButton(self.dockWidgetContents)
        self.nextButton.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("images/next.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.nextButton.setIcon(icon2)
        self.nextButton.setAutoDefault(True)
        self.nextButton.setObjectName("nextButton")
        self.horizontalLayout_2.addWidget(self.nextButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.dockWidget.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dockWidget)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionMenuQuit = QtWidgets.QAction(MainWindow)
        self.actionMenuQuit.setObjectName("actionMenuQuit")
        self.actionNewScreen = QtWidgets.QAction(MainWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("images/new_screen.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionNewScreen.setIcon(icon3)
        self.actionNewScreen.setText("")
        self.actionNewScreen.setObjectName("actionNewScreen")
        self.actionMenuSettings = QtWidgets.QAction(MainWindow)
        self.actionMenuSettings.setObjectName("actionMenuSettings")
        self.actionMenuNewScreen = QtWidgets.QAction(MainWindow)
        self.actionMenuNewScreen.setObjectName("actionMenuNewScreen")
        self.menu_File.addAction(self.actionMenuNewScreen)
        self.menu_File.addAction(self.actionMenuSettings)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.actionMenuQuit)
        self.menubar.addAction(self.menu_File.menuAction())
        self.toolBar.addAction(self.actionNewScreen)

        self.retranslateUi(MainWindow)
        self.actionMenuQuit.triggered.connect(MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "PyKaraokeServer"))
        self.SearchLabel.setText(_translate("MainWindow", "Search"))
        self.menu_File.setTitle(_translate("MainWindow", "&File"))
        self.label_2.setText(_translate("MainWindow", "Playlist"))
        self.playButton.setToolTip(_translate("MainWindow", "Play"))
        self.playButton.setShortcut(_translate("MainWindow", "Ctrl+P"))
        self.stopButton.setToolTip(_translate("MainWindow", "Stop"))
        self.stopButton.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.nextButton.setToolTip(_translate("MainWindow", "Next song"))
        self.nextButton.setShortcut(_translate("MainWindow", "Ctrl+N"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.actionMenuQuit.setText(_translate("MainWindow", "&Quit"))
        self.actionNewScreen.setToolTip(_translate("MainWindow", "New screen"))
        self.actionNewScreen.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.actionMenuSettings.setText(_translate("MainWindow", "&Settings..."))
        self.actionMenuNewScreen.setText(_translate("MainWindow", "New Lyrics Window"))

from widgets import PlaylistTableView
