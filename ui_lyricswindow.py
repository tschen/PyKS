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

# Form implementation generated from reading ui file 'lyrics_window.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_LyricsWindow(object):
    def setupUi(self, LyricsWindow):
        LyricsWindow.setObjectName("LyricsWindow")
        LyricsWindow.resize(300, 216)
        LyricsWindow.setMinimumSize(QtCore.QSize(300, 216))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/new_screen.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        LyricsWindow.setWindowIcon(icon)

        self.retranslateUi(LyricsWindow)
        QtCore.QMetaObject.connectSlotsByName(LyricsWindow)

    def retranslateUi(self, LyricsWindow):
        _translate = QtCore.QCoreApplication.translate
        LyricsWindow.setWindowTitle(_translate("LyricsWindow", "PyKS"))

