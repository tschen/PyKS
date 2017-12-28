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
# PyQt5 imports
from PyQt5 import QtCore, QtGui, QtNetwork, QtSql, QtWidgets

# Python3 std lib imports
import configparser
import pickle

# PyKS imports
from ui_aboutdialog import Ui_AboutDialog
from ui_addtoplaylistdialog import Ui_AddToPlaylistDialog
from ui_alertdialog import Ui_AlertDialog
from ui_settingsdialog import Ui_SettingsDialog


# This is a special QTableView that emits a signal when the Del key is
# pressed, allowing us to remove songs with the keyboard.
class SonglistTableView (QtWidgets.QTableView):
    removeSongs = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(SonglistTableView, self).__init__(parent)


    def keyPressEvent(self, event):
        super(SonglistTableView, self).keyPressEvent(event)
        if event.key() == QtCore.Qt.Key_Delete:
            self.removeSongs.emit()


class AddToPlaylistDialog (QtWidgets.QDialog, Ui_AddToPlaylistDialog):

    def __init__(self, songs, performersName, alwaysUseName, parent=None):
        super(AddToPlaylistDialog, self)\
            .__init__(parent, QtCore.Qt.WindowTitleHint
                              | QtCore.Qt.WindowCloseButtonHint)
        self.setupUi(self)
        self.addToPlaylistTextEdit.setText('\n'.join(songs))
        self.performerNameLineEdit.setText(performersName)
        self.alwaysUseNameCheckbox.setChecked(alwaysUseName)


class AlertDialog (QtWidgets.QDialog, Ui_AlertDialog):

    def __init__(self, title, text, parent=None):
        super(AlertDialog, self)\
                .__init__(parent, QtCore.Qt.WindowTitleHint
                                  | QtCore.Qt.WindowCloseButtonHint)
        self.setupUi(self)
        self.setWindowTitle(title)
        self.alertMsg.setText(text)


class Settings (object):
    DEFAULT_PERFORMER_MODE = True
    DEFAULT_QUEUE_ON_STARTUP = True
    DEFAULT_SECONDS_TO_WAIT = -1
    DEFAULT_SERVER_ON_STARTUP = False
    DEFAULT_HOST_ADDRESS = "0.0.0.0"
    DEFAULT_HOST_PORT = 0
    DEFAULT_ADMIN_PASSWORD = "password"
    DEFAULT_ALLOW_MULTIPLE_CONNECTIONS = False
    DEFAULT_MAX_CONNECTED_CLIENTS = -1

    DEFAULT_SEARCH_FOLDERS = []

    def __init__(self,
                 performerMode=DEFAULT_PERFORMER_MODE,
                 queueOnStartup = DEFAULT_QUEUE_ON_STARTUP,
                 secondsToWait=DEFAULT_SECONDS_TO_WAIT,
                 serverOnStartup=DEFAULT_SERVER_ON_STARTUP,
                 hostAddress=DEFAULT_HOST_ADDRESS,
                 hostPort=DEFAULT_HOST_PORT,
                 adminPassword=DEFAULT_ADMIN_PASSWORD,
                 maxConnectedClients=DEFAULT_MAX_CONNECTED_CLIENTS,
                 allowMultipleConnections = DEFAULT_ALLOW_MULTIPLE_CONNECTIONS,
                 searchFolders=DEFAULT_SEARCH_FOLDERS):

        # General Settings
        self.performerMode = performerMode
        self.queueOnStartup = queueOnStartup
        self.secondsToWait = secondsToWait

        # Server settings
        self.serverOnStartup = serverOnStartup
        self.hostAddress = hostAddress
        self.hostPort = hostPort
        self.adminPassword = adminPassword
        self.allowMultipleConnections = allowMultipleConnections
        self.maxConnectedClients = maxConnectedClients

        # Database settings
        self.searchFolders = searchFolders

        # Session settings
        # These settings are only used while PyKS is running and are not saved
        # in the ini file.
        self.alwaysUsePerformersName = False
        self.defaultPerformerName = ""


    def readSettings(iniFile):

        settings = Settings()

        # Attempt to read in settings file. ConfigParser.read() returns
        # a list of successfully read filenames. If the list is not empty,
        # use those values. Otherwise, use default values.
        config = configparser.ConfigParser()
        if config.read(iniFile):

            # For each setting, try to read its value from the ini file. If the
            # parsing fails, use the default value.

            # General settings
            try:
                settings.performerMode = config.getboolean('General',
                                                                'PerformerMode')
            except:
                settings.performerMode = Settings.DEFAULT_PERFORMER_MODE

            try:
                settings.queueOnStartup = config.getboolean('General',
                                                       'QueueOnStartup')

            except:
                settings.performerMode = Settings.DEFAULT_QUEUE_ON_STARTUP

            try:
                settings.secondsToWait = config.getint('General',
                                                       'SecondsToWait')
            except:
                settings.secondsToWait = Settings.DEFAULT_SECONDS_TO_WAIT


            # Server settings
            try:
                settings.serverOnStartup = \
                    config.getboolean('Server', 'ServerOnStartup')
            except:
                settings.serverOnStartup = \
                    Settings.DEFAULT_SERVER_ON_STARTUP

            try:
                settings.hostAddress = config.get('Server', 'HostAddress')
            except:
                settings.hostAddress = Settings.DEFAULT_HOST_ADDRESS

            try:
                settings.hostPort = config.getint('Server', 'HostPort')
            except:
                settings.hostPort = Settings.DEFAULT_HOST_PORT

            try:
                settings.adminPassword = \
                    config.get('Server', 'AdminPassword')
            except:
                settings.adminPassword = Settings.DEFAULT_ADMIN_PASSWORD

            try:
                settings.allowMultipleConnections = \
                    config.getboolean('Server', 'AllowMultipleConnections')
            except:
                settings.allowMultipleConnections = \
                    Settings.DEFAULT_ALLOW_MULTIPLE_CONNECTIONS

            try:
                settings.maxConnectedClients = \
                    config.getint('Server', 'MaxConnectedClients')
            except:
                settings.maxConnectedClients = \
                    Settings.DEFAULT_MAX_CONNECTED_CLIENTS


            # Database settings
            try:
                settings.searchFolders = \
                    config.get('Database', 'SearchFolderList')
            except:
                settings.searchFolders = Settings.DEFAULT_SEARCH_FOLDERS
            # If searchFolder is not an empty string or empty list (i.e. it's
            # a string of folder values separated by commas), convert it into
            # a list. Otherwise, set it to an empty list.
            if settings.searchFolders:
                settings.searchFolders = \
                    settings.searchFolders.split(', ')
            else:
                settings.searchFolders = []

            return settings


    def writeSettings(newSettings, iniFile):
        config = configparser.ConfigParser()
        # keep ConfigParser from converting keys to lowercase
        config.optionxform = str

        # General settings
        config['General'] = {'PerformerMode': newSettings.performerMode,
                             'QueueOnStartup':
                                 newSettings.queueOnStartup,
                             'SecondsToWait': newSettings.secondsToWait}

        # Server settings
        config['Server'] = {'ServerOnStartup': newSettings.serverOnStartup,
                            'HostAddress': newSettings.hostAddress,
                            'HostPort': newSettings.hostPort,
                            'AdminPassword': newSettings.adminPassword,
                            'AllowMultipleConnections':
                                newSettings.allowMultipleConnections,
                            'MaxConnectedClients':
                                newSettings.maxConnectedClients}

        # Database settings
        config['Database'] = {
            'SearchFolderList': (', ').join(newSettings.searchFolders)}

        try:
            configFile = open(iniFile, 'w')
            config.write(configFile)
        except:
            # Warn user that we can't save their settings
            alert = AlertDialog("File Error",
                                 "Could not save settings to '%s'" % iniFile)
            alert.exec()


class AboutDialog (QtWidgets.QDialog, Ui_AboutDialog):
    ABOUT_PAGE = 0
    LICENSE_PAGE = 1
    CREDITS_PAGE = 2

    def __init__(self, version, parent=None):
        super(AboutDialog, self).__init__(parent)
        self.setupUi(self)

        # Set version
        self.versionLabel.setText(str(version))

        # Setup the License and Credits buttons
        self.licenseButton.clicked.connect(self.licenseClicked)
        self.creditsButton.clicked.connect(self.creditsClicked)
        self.okButton.clicked.connect(self.close)

        self.changeAboutsMenu(AboutDialog.ABOUT_PAGE)

    def changeAboutsMenu(self, index):
        self.stackedWidget.setCurrentIndex(index)

    def creditsClicked(self):
        self.changeAboutsMenu(AboutDialog.CREDITS_PAGE)

    def licenseClicked(self):
        self.changeAboutsMenu(AboutDialog.LICENSE_PAGE)


class SettingsDialog (QtWidgets.QDialog, Ui_SettingsDialog):
    updateDatabaseClicked = QtCore.pyqtSignal(list)

    def __init__(self, curSettings, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setupUi(self)

        # Setup navigation pane with a list of settings
        self.settingsList.addItems(['General', 'Server', 'Database'])
        self.settingsList.currentRowChanged.connect(self.changeSettingMenu)
        # Highlight the first in the list
        self.settingsList.setCurrentRow(0)

        # General settings
        self.performerModeCheckBox.setChecked(curSettings.performerMode)
        self.queueOnStartupCheckBox.setChecked(
            curSettings.queueOnStartup)
        if not self.performerModeCheckBox.isChecked():
            self.queueOnStartupCheckBox.setEnabled(False)

        self.secondsToWaitTextBox.setText(str(curSettings.secondsToWait))

        # Server settings
        self.hostAddressTextBox.setText(curSettings.hostAddress)
        self.hostPortTextBox.setText(str(curSettings.hostPort))
        self.serverOnStartupCheckBox.setChecked(curSettings.serverOnStartup)
        self.adminPasswordTextBox.setText(curSettings.adminPassword)
        self.allowMultipleConnectionsCheckBox.setChecked(
            curSettings.allowMultipleConnections)
        self.maxConnectedClientsTextBox.setText(
            str(curSettings.maxConnectedClients))
        self.autoDetectButton.clicked.connect(self.autoDetectNetworkInterface)


        # Database settings
        self.searchFolderList.addItems(curSettings.searchFolders)

        self.browseButton.clicked.connect(self.browseClicked)
        self.removeButton.clicked.connect(self.removeClicked)
        self.updDatabaseButton.clicked.connect(self.updDatabaseClicked)

        self.performerModeCheckBox.stateChanged.connect(
            self.processPerformerModeStateChanged)

        self.newSettings = Settings()


    def accept(self):
        # On accept, save all the new settings
        self.newSettings.performerMode = self.performerModeCheckBox.isChecked()
        self.newSettings.queueOnStartup = \
            self.queueOnStartupCheckBox.isChecked()
        self.newSettings.secondsToWait = int(self.secondsToWaitTextBox.text())

        self.newSettings.hostAddress = self.hostAddressTextBox.text()
        self.newSettings.hostPort = int(self.hostPortTextBox.text())
        self.newSettings.serverOnStartup = \
            self.serverOnStartupCheckBox.isChecked()
        self.newSettings.adminPassword = self.adminPasswordTextBox.text()
        self.newSettings.allowMultipleConnections = \
            self.allowMultipleConnectionsCheckBox.isChecked()
        self.newSettings.maxConnectedClients = int(
            self.maxConnectedClientsTextBox.text())

        self.newSettings.searchFolders = []
        for i in range (self.searchFolderList.count()):
            self.newSettings.searchFolders.append(self.searchFolderList.item(
                i).data(0))

        super(SettingsDialog, self).accept()


    def getSettings(self):
        return self.newSettings


    @QtCore.pyqtSlot(int)
    def processPerformerModeStateChanged(self, state):
        if self.performerModeCheckBox.isChecked():
            self.queueOnStartupCheckBox.setEnabled(True)
        else:
            self.queueOnStartupCheckBox.setEnabled(False)


    @QtCore.pyqtSlot(int)
    def changeSettingMenu (self, index):
        self.stackedWidget.setCurrentIndex(index)


    @QtCore.pyqtSlot()
    def autoDetectNetworkInterface(self):
        hostAddresses = []
        interfaceFlags = QtNetwork.QNetworkInterface.IsUp | \
                          QtNetwork.QNetworkInterface.IsRunning
        # Grab all available interfaces
        allInterfaces = QtNetwork.QNetworkInterface.allInterfaces()
        for interface in allInterfaces:
            if ((interface.flags() & interfaceFlags == interfaceFlags) \
                ):#and (interface.flags() &
                 #           QtNetwork.QNetworkInterface.IsLoopBack == 0)):
                addresses = interface.addressEntries()
                for address in addresses:
                    if (address.ip().protocol() ==
                            QtNetwork.QAbstractSocket.IPv4Protocol) and \
                                    address.ip() != (
                                    QtNetwork.QHostAddress(
                                        QtNetwork.QHostAddress.LocalHost)):
                        hostAddresses.append(address.ip())
                        # If there is more than one host address detected,
                        # show error dialog
                        if len(hostAddresses) > 1:
                            alert = AlertDialog("Network Error",
                                                "Could not auto detect network "
                                                "settings")
                            alert.show()
                        else: # only one IP address returned, try port 80
                            testServer = QtNetwork.QTcpServer(self)
                            # Try to start a QTcpServer at hostAddress:80
                            # If the server starts, return those values as
                            # detected values
                            if testServer.listen(hostAddresses[0], 80):
                                ipAddress = hostAddresses[0].toString()
                                # populate server text boxes
                                self.hostAddressTextBox.setText(ipAddress)
                                self.hostPortTextBox.setText(str(80))
                                testServer.close()
                            else:
                                # Could not listen at detected IP address and
                                # port 80. This may be because port 80 is
                                # being used by another service, so let
                                # QTcpServer pick the port.
                                if testServer.listen(hostAddresses[0]):
                                    ipAddress = hostAddresses[0].toString()
                                    port = testServer.serverPort()
                                    # populate server text boxes
                                    self.hostAddressTextBox.setText(ipAddress)
                                    self.hostPortTextBox.setText(str(port))
                                    testServer.close()
                                else: # Can't auto detect network settings
                                    alert = AlertDialog("Network Error",
                                                        "Could not auto "
                                                        "detect  network "
                                                        "settings")
                                    alert.show()


    @QtCore.pyqtSlot()
    def browseClicked(self):
        dialog = QtWidgets.QFileDialog(self, caption="Select folders", directory="./")
        dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        dialog.setOptions(QtWidgets.QFileDialog.ShowDirsOnly)
        dialog.setViewMode(QtWidgets.QFileDialog.List)
        if dialog.exec():
            self.searchFolderList.addItems(dialog.selectedFiles())


    @QtCore.pyqtSlot()
    def removeClicked(self):
        items = self.searchFolderList.selectedItems()
        for item in items:
            self.searchFolderList.takeItem(self.searchFolderList.row(item))


    @QtCore.pyqtSlot()
    def updDatabaseClicked(self):
        # Grab the list of folders and emit the updateDatabaseClicked signal
        searchFolders = []
        for i in range (self.searchFolderList.count()):
            searchFolders.append(self.searchFolderList.item(i).data(0))
        self.updateDatabaseClicked.emit(searchFolders)


# Adapted from
# https://stackoverflow.com/questions/21232224/qlineedit-with-custom-button
class SearchBox(QtWidgets.QLineEdit):
    def __init__(self, parent=None):
        super(SearchBox, self).__init__(parent)

        self.clearButton = QtWidgets.QToolButton(self)
        pixmap = QtGui.QPixmap("images/clear.png")

        self.clearButton.setIcon(QtGui.QIcon(pixmap))
        self.clearButton.setIconSize(pixmap.size()/1.5)
        self.clearButton.setCursor(QtCore.Qt.ArrowCursor)
        self.clearButton.setStyleSheet(
            "QToolButton {border: none; padding: 0px;}")
        self.clearButton.hide()

        self.clearButton.clicked.connect(self.clear)
        self.textChanged.connect(self.updateCloseButton)

        frameWidth = self.style().pixelMetric(
            QtWidgets.QStyle.PM_DefaultFrameWidth)
        self.setStyleSheet("QLineEdit { padding-right: %dpx; }" %
                           (self.clearButton.sizeHint().width()
                            + frameWidth + 1))
        msz = self.minimumSizeHint()
        self.setMinimumSize(max(msz.width(),
                                self.clearButton.sizeHint().height()
                                + frameWidth * 2 + 2),
                            max(msz.height(),
                                self.clearButton.sizeHint().height()
                                + frameWidth * 2 + 2))

    def resizeEvent(self, event):
        sz = self.clearButton.sizeHint()
        frameWidth = self.style().pixelMetric(
            QtWidgets.QStyle.PM_DefaultFrameWidth)
        self.clearButton.move(self.rect().right() - frameWidth - sz.width(),
                              (self.rect().bottom() + 1 - sz.height())/2)


    # Clear text box on Esc
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.clear()
        super(SearchBox, self).keyPressEvent(event)


    def updateCloseButton(self, text):
        if not self.text():
            self.clearButton.setVisible(False)
        else:
            self.clearButton.setVisible(True)


class SonglistModel (QtCore.QAbstractTableModel):
    songlistUpdated = QtCore.pyqtSignal(list)
    dropAction = QtCore.pyqtSignal(dict)

    NUM_COLS = 4
    QUEUE_NUM_COL = 0
    PERF_COL = 1
    SONG_NAME_COL = 2
    SONG_ID_COL = 3

    PERFORMER = 0
    SONG_NAME = 1
    SONG_ID = 2

    def __init__(self, parent=None):
        super(SonglistModel, self).__init__(parent)
        # The song list is represented by a list of tuples containing the
        # the following:
        # (performer, song name, song ID)
        self.songlist = []


    def removeRows(self, row, count, parent=None):
        self.removeSongs(list(range(row, row + count)))
        return True


    def removeRow(self, row, parent=None):
        self.removeRows(row, 1, parent)
        return True


    def rowCount(self, parent=None):
        return len(self.songlist)


    def columnCount(self, parent=None):
        return self.NUM_COLS


    def headerData(self, section, orientation, role=None):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if section == self.QUEUE_NUM_COL:
                    return "#"

                if section == self.PERF_COL:
                    return "Performer"

                if section == self.SONG_NAME_COL:
                    return "Song Name"

                return ""


    def data(self, index, role=None):
        if role == QtCore.Qt.DisplayRole:
            if index.column() == self.QUEUE_NUM_COL:
                return str(index.row() + 1)
            return self.songlist[index.row()][index.column() - 1]


    def flags(self, index):
        defaultFlags = super(SonglistModel, self).flags(index)

        if index.isValid():
            return QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled \
                   | defaultFlags
        else:
            return QtCore.Qt.ItemIsDropEnabled | defaultFlags

    def supportedDropActions(self):
        return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction


    def mimeTypes(self):
        return ["application/prs.song"]


    def mimeData(self, indexes):
         mimeData = QtCore.QMimeData()
         dragDropData = {'indexes':[], 'songs':[]}
         for index in indexes:
             # indexes will return a QModelIndex for each (row, column) item in
             # our table. This means that there will be multiple indexes for
             # each row, one for each of the table's columns. Since we only care
             # about rows and not columns, don't store the item if we've already
             # seen the row.
             if index.row() not in dragDropData['indexes']:
                 dragDropData['indexes'].append(index.row())
                 dragDropData['songs'].append(self.songlist[index.row()])
         mimeData.setData("application/prs.song", pickle.dumps(dragDropData))
         return mimeData


    def dropMimeData(self, data, action, row, column, parent):
        # Only accept our special MIME types
        if (not data.hasFormat("application/prs.song")):
            return False

        if (column > 0):
            return False;

        if action == QtCore.Qt.IgnoreAction:
            return True

        # We pass our MIME data as a byte stream representing a pickled python
        # dictionary. When we receive the data on a drop action, turn it
        # back into a dictionary.
        dragDropData = pickle.loads(data.data("application/prs.song"))

        # If this is a MoveAction, remove the songs and reinsert them.
        if action == QtCore.Qt.MoveAction:
            # First remove songs
            #self.removeSongs(dragDropData['indexes'])

            # Next insert songs
            if (parent.row() == -1):
                self.appendSongs(dragDropData['songs'])
            else:
                self.insertSongs(parent.row(), dragDropData['songs'])
        else:
            # If this is not an internal move, copy the drop location
            # into dragDropData and emit a signal with the
            # with the drop data to let PyKS take care of the drop action.
            dragDropData['indexes'] = parent.row()

            self.dropAction.emit(dragDropData)
        return True


    def appendSongs(self, songs):
        self.insertSongs(len(self.songlist), songs)


    def insertSongs(self, position, songs):
        self.beginInsertRows(QtCore.QModelIndex(), position,
                             position + (len(songs) - 1))
        for song in songs:
            self.songlist.insert(position, song)
            position += 1
        self.endInsertRows()

        self.songlistUpdated.emit(self.songlist)


    def removeSongs(self, songPostions):
        numRemoved = 0

        for pos in songPostions:
            pos = pos - numRemoved
            self.beginRemoveRows(QtCore.QModelIndex(), pos, pos)
            del (self.songlist[pos])
            self.endRemoveRows()
            numRemoved += 1

        self.songlistUpdated.emit(self.songlist)


    def getCurSong(self):
        if len(self.songlist):
            return self.songlist[0]
        else:
            return None


    def getNextSong(self):
        if len (self.songlist):
            self.removeSongs([0])
            return self.getCurSong()


    def getSonglist(self):
        return self.songlist


class DragDropSqlQueryModel (QtSql.QSqlQueryModel):
    NUM_COLS = 3
    ARTIST_COL = 0
    TITLE_COL = 1
    SONG_ID_COL = 2

    def flags(self, index):
        defaultFlags = super(DragDropSqlQueryModel, self).flags(index)

        if index.isValid():
            return QtCore.Qt.ItemIsDragEnabled | defaultFlags
        else:
            return defaultFlags


    def mimeTypes(self):
        return ["application/prs.song"]


    def mimeData(self, indexes):
        mimeData = QtCore.QMimeData()
        dragDropData = {'indexes':[], 'songs':[]}
        rows = []

        for index in indexes:
            # indexes will return a QModelIndex for each (row, column) item in
            # our table. This means that there will be multiple indexes for
            # each row, one for each of the table's columns. Since we only care
            # about rows and not columns, don't store the item if we've already
            # seen the row.
            if index.row() not in rows:
                rows.append(index.row())
                # songs are a list of [artist - title, SONG ID] lists
                dragDropData['songs'].append(
                    [''.join([
                         self.index(index.row(), self.ARTIST_COL).data(),
                         ' - ',
                         self.index(index.row(), self.TITLE_COL).data()]),
                     self.index(index.row(), self.SONG_ID_COL).data()])

        mimeData.setData("application/prs.song", pickle.dumps(dragDropData))
        return mimeData
