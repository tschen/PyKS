# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'addtoplaylist_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AddToPlaylistDialog(object):
    def setupUi(self, AddToPlaylistDialog):
        AddToPlaylistDialog.setObjectName("AddToPlaylistDialog")
        AddToPlaylistDialog.resize(448, 326)
        self.buttonBox = QtWidgets.QDialogButtonBox(AddToPlaylistDialog)
        self.buttonBox.setGeometry(QtCore.QRect(50, 270, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.label = QtWidgets.QLabel(AddToPlaylistDialog)
        self.label.setGeometry(QtCore.QRect(20, 20, 291, 20))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.performerNameLineEdit = QtWidgets.QLineEdit(AddToPlaylistDialog)
        self.performerNameLineEdit.setGeometry(QtCore.QRect(140, 200, 241, 20))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.performerNameLineEdit.setFont(font)
        self.performerNameLineEdit.setObjectName("performerNameLineEdit")
        self.label_3 = QtWidgets.QLabel(AddToPlaylistDialog)
        self.label_3.setGeometry(QtCore.QRect(30, 200, 111, 16))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.addToPlaylistTextEdit = QtWidgets.QTextEdit(AddToPlaylistDialog)
        self.addToPlaylistTextEdit.setGeometry(QtCore.QRect(60, 50, 321, 131))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.addToPlaylistTextEdit.sizePolicy().hasHeightForWidth())
        self.addToPlaylistTextEdit.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.addToPlaylistTextEdit.setFont(font)
        self.addToPlaylistTextEdit.setUndoRedoEnabled(False)
        self.addToPlaylistTextEdit.setReadOnly(True)
        self.addToPlaylistTextEdit.setObjectName("addToPlaylistTextEdit")
        self.alwaysUseNameCheckbox = QtWidgets.QCheckBox(AddToPlaylistDialog)
        self.alwaysUseNameCheckbox.setGeometry(QtCore.QRect(140, 230, 171, 17))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.alwaysUseNameCheckbox.setFont(font)
        self.alwaysUseNameCheckbox.setObjectName("alwaysUseNameCheckbox")

        self.retranslateUi(AddToPlaylistDialog)
        self.buttonBox.accepted.connect(AddToPlaylistDialog.accept)
        self.buttonBox.rejected.connect(AddToPlaylistDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AddToPlaylistDialog)

    def retranslateUi(self, AddToPlaylistDialog):
        _translate = QtCore.QCoreApplication.translate
        AddToPlaylistDialog.setWindowTitle(_translate("AddToPlaylistDialog", "Add To Playlist"))
        self.label.setText(_translate("AddToPlaylistDialog", "Add the following song(s) to the playlist?"))
        self.label_3.setText(_translate("AddToPlaylistDialog", "For Performer:"))
        self.alwaysUseNameCheckbox.setText(_translate("AddToPlaylistDialog", "Always use this name"))

