# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'alert_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AlertDialog(object):
    def setupUi(self, AlertDialog):
        AlertDialog.setObjectName("AlertDialog")
        AlertDialog.setWindowModality(QtCore.Qt.NonModal)
        AlertDialog.resize(412, 117)
        AlertDialog.setModal(True)
        self.buttonBox = QtWidgets.QDialogButtonBox(AlertDialog)
        self.buttonBox.setGeometry(QtCore.QRect(40, 70, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.alertMsg = QtWidgets.QLabel(AlertDialog)
        self.alertMsg.setGeometry(QtCore.QRect(30, 20, 351, 41))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(False)
        font.setWeight(50)
        self.alertMsg.setFont(font)
        self.alertMsg.setText("")
        self.alertMsg.setAlignment(QtCore.Qt.AlignCenter)
        self.alertMsg.setWordWrap(True)
        self.alertMsg.setObjectName("alertMsg")

        self.retranslateUi(AlertDialog)
        self.buttonBox.accepted.connect(AlertDialog.accept)
        self.buttonBox.rejected.connect(AlertDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AlertDialog)

    def retranslateUi(self, AlertDialog):
        _translate = QtCore.QCoreApplication.translate
        AlertDialog.setWindowTitle(_translate("AlertDialog", "Dialog"))

