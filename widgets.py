# PyQt5 imports
from PyQt5 import QtCore, QtGui, QtNetwork, QtWidgets

# Python3 std lib imports
import configparser

# PyKS imports
from ui_addtoplaylistdialog import Ui_AddToPlaylistDialog
from ui_alertdialog import Ui_AlertDialog
from ui_lyricswindow import Ui_LyricsWindow
from ui_settingsdialog import Ui_SettingsDialog

class LyricsWindow(QtWidgets.QMainWindow, Ui_LyricsWindow):
    closedWindow = QtCore.pyqtSignal()

    def __init__(self, cdgPlayer, parent=None):
        super(LyricsWindow, self).__init__(parent)
        self.setupUi(self)
        # WA_OpaquePaintEvent indicates that the widget paints all its pixels
        # when it recevies a paint event, so it's not necessary to erase the
        # widget before generating paint events.
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
        self.cdgPlayer = cdgPlayer
        self.cdgImage = cdgPlayer.getCdgImage()
        self.cdgPlayer.cdgImageUpdated.connect(self.update)


    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawImage(event.rect(), self.cdgImage)


    def mouseDoubleClickEvent(self, event):
        # If double click was generated by a left click, toggle the size of
        # the window
        if event.button() == QtCore.Qt.LeftButton:
            if self.isFullScreen():
                self.showNormal()
                # Set the cursor to be visible
                self.setCursor(QtCore.Qt.ArrowCursor)
            else:
                self.showFullScreen()
                # Set the cursor to be invisible
                self.setCursor(QtCore.Qt.BlankCursor)


    def keyPressEvent(self, event):
        # If Esc is pressed in full sreen mode, return to normal mode
        if (event.key() == QtCore.Qt.Key_Escape and self.isFullScreen()):
            self.showNormal()
            # Set the cursor to be visible
            self.setCursor(QtCore.Qt.ArrowCursor)


    # Signal when the window is closed
    def closeEvent(self, event):
        self.closedWindow.emit()


# This is a special TableView that emits a signal when the Del key is
# pressed, allowing us to remove songs with the keyboard.
class PlaylistTableView (QtWidgets.QTableView):
    removeSongs = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(PlaylistTableView, self).__init__(parent)


    def keyPressEvent(self, event):
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
                             'SecondsToWait': newSettings.secondsToWait}

        # Server settings
        config['Server'] = {'ServerOnStartup': newSettings.serverOnStartup,
                            'HostAddress': newSettings.hostAddress,
                            'HostPort': newSettings.hostPort,
                            'AdminPassword': newSettings.adminPassword,
                            'AllowMultpleConnections':
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

        self.newSettings = Settings()


    def accept(self):
        # On accept, save all the new settings
        self.newSettings.performerMode = self.performerModeCheckBox.isChecked()
        self.newSettings.secondsToWait = self.secondsToWaitTextBox.text()

        self.newSettings.hostAddress = self.hostAddressTextBox.text()
        self.newSettings.hostPort = int (self.hostPortTextBox.text())
        self.newSettings.serverOnStartup = \
            self.serverOnStartupCheckBox.isChecked()
        self.newSettings.adminPassword = self.adminPasswordTextBox.text()
        self.newSettings.allowMultipleConnections = \
            self.allowMultipleConnectionsCheckBox.isChecked()
        self.newSettings.maxConnectedClients = int (
            self.maxConnectedClientsTextBox.text())

        self.newSettings.searchFolders = []
        for i in range (self.searchFolderList.count()):
            self.newSettings.searchFolders.append(self.searchFolderList.item(
                i).data(0))

        super(SettingsDialog, self).accept()


    def getSettings(self):
        return self.newSettings


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
            if (interface.flags() & interfaceFlags == interfaceFlags):
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
