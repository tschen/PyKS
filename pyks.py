# PyQt5 imports
from PyQt5 import QtCore, QtGui, QtNetwork, QtSql, QtWidgets

# Python3 std lib imports
import collections
import json
import os
import re
import sys
import time

# PyKS imports
from cdg import CdgPlayer
from server import KaraokeServer
from ui_mainwindow import Ui_MainWindow
from widgets import AddToPlaylistDialog, AlertDialog, \
    LyricsWindow, Settings, SettingsDialog


class PlaylistModel (QtCore.QAbstractTableModel):
    playlistUpdated = QtCore.pyqtSignal(list)

    NUM_COLS = 4
    QUEUE_NUM_COL = 0
    PERF_COL = 1
    SONG_NAME_COL = 2
    SONG_ID_COL = 3

    PERFORMER = 0
    SONG_NAME = 1
    SONG_ID = 2

    def __init__(self, parent=None):
        super(PlaylistModel, self).__init__(parent)
        # The playlist is represented by a list of tuples containing the
        # the following:
        # (performer, song name, song ID)
        self.playlist = []


    def rowCount(self, parent=None):
        return len (self.playlist)


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
                return str(index.row()+1)
            return self.playlist[index.row()][index.column()-1]


    def appendSongs(self, songs):
        self.insertSongs(len(self.playlist), songs)


    def insertSongs(self, position, songs):
        self.beginInsertRows(QtCore.QModelIndex(), position,
                             position + (len(songs) - 1))
        for song in songs:
            self.playlist.insert(position, song)
            position += 1
        self.endInsertRows()
        self.playlistUpdated.emit(self.playlist)


    def removeSong(self, position):
        self.beginRemoveRows(QtCore.QModelIndex(), position, position)
        del (self.playlist[position])
        self.endRemoveRows()
        self.playlistUpdated.emit(self.playlist)


    def getCurSong(self):
        if len(self.playlist):
            return self.playlist[0]
        else:
            return None


    def getNextSong(self):
        if len (self.playlist):
            self.removeSong(0)
            return self.getCurSong()


class PyKS(QtWidgets.QMainWindow, Ui_MainWindow):
    SETTINGS_FILE = 'pyks.ini'
    SONGBOOK_DB_FILE = 'songbook.db'
    SONGBOOK_JSON_FILE = 'sonbook.json'

    NUM_COLS = 3
    ARTIST_COL = 0
    TITLE_COL = 1
    SONG_ID_COL = 2

    songbookUpdated = QtCore.pyqtSignal('QString')

    def __init__(self, parent=None):
        super(PyKS, self).__init__(parent)

        # Run Ui_MainWindow.setupUi() to set up the main window
        self.setupUi(self)

        # On startup, import settings from pyks.ini if the file exists.
        # If the file does not exist, create it with default settings.
        if os.path.isfile(self.SETTINGS_FILE):
            self.settings = Settings.readSettings(self.SETTINGS_FILE)
        else:
            # Create default settings
            self.settings = Settings()
            # Write settings to ini file
            Settings.writeSettings(self.settings, self.SETTINGS_FILE)

        # The songbook is stored as a SQLite database and as a JSON file on
        # disk. The SQLLite database is used by the main app while the JSON
        # file is used by the web app. On startup try to open both database
        # files. If either databse does not exist, create it by searching
        # through files found in self.settings.searchFolders.
        self.songbookdb = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        self.songbookdb.setDatabaseName(self.SONGBOOK_DB_FILE)

        if not os.path.isfile(self.SONGBOOK_DB_FILE) or not os.path.isfile(
                self.SONGBOOK_JSON_FILE):
            self._createSongbook(self.settings.searchFolders)

        # We close the database when the app closes
        self.songbookdb.open()

        # Open the JSON file and read in its contents
        self.songbookJSON = open (self.SONGBOOK_JSON_FILE, 'r').read()

        # Setup search results panel
        # The underlying model holding the data displayed by
        # searchResultsListView is a QSqlQueryModel contained in a
        # QSortFilterProxyModel to allow for sorting.
        #FIXME should this be in its own function?
        self.sqlQueryModel = QtSql.QSqlQueryModel(self)
        self.sqlQueryModel.setQuery\
            ('SELECT artist, title, songID from songs')
        # QSqlQueryModel only fetches 256 rows at a time
        # Keep fetching until all rows are fetched
        while (self.sqlQueryModel.canFetchMore()):
            self.sqlQueryModel.fetchMore()


        # Set up QSortFilterProxyModel to allow for sorting
        self.sortFilterProxyModel = QtCore.QSortFilterProxyModel(self)
        self.sortFilterProxyModel.setSourceModel(self.sqlQueryModel)
        self.sortFilterProxyModel.setHeaderData(self.ARTIST_COL,
                                          QtCore.Qt.Horizontal, 'Artist')
        self.sortFilterProxyModel.setHeaderData(self.TITLE_COL,
                                           QtCore.Qt.Horizontal, 'Title')

        # Set the searchResultsTableView to use srtFilterProxyModel as its
        # underlying data container
        self.searchResultsTableView.setModel(self.sortFilterProxyModel)
        # Hide the first column of row numbers
        self.searchResultsTableView.verticalHeader().setVisible(False)
        # Initially set sorting to be by artist
        self.searchResultsTableView.sortByColumn(self.ARTIST_COL,
                                                 QtCore.Qt.AscendingOrder)
        # Hide Song ID column
        self.searchResultsTableView.hideColumn(self.SONG_ID_COL)
        # Set QTableView selection behavior to select only rows
        self.searchResultsTableView.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows)
        self.searchResultsTableView.resizeColumnsToContents()
        # searchResultsTableView Signal/Slot
        self.searchResultsTableView.activated.connect(self.addToPlaylist)
        self.searchResultsTableView.customContextMenuRequested.connect(
            self.showSearchResultsContextMenu)

        # Setup the searchLineEdit to perform searches as the user types.
        # The keypressTimer is a singleshot timer used to delay executing
        # search queries until the user has stopped typing for specified period
        # of time. This prevents us from flooding the database with search
        # queries.
        self.__keypressTimer = QtCore.QTimer()
        self.__keypressTimer.setSingleShot(True)
        self.__keypressTimer.timeout.connect(self.processSearch)
        self.searchLineEdit.textChanged.connect (self.startKeypressTimer)

        # Setup the playlist panel
        # The playlist is a list of tuples where each tuple contains the
        # following:
        # (performer's name, song name, song ID)
        # The playlist data structure is contained in a PlaylistModel and is
        # manipulated through calls to the model's methods.
        self.playlistModel = PlaylistModel(self)
        self.playlistTableView.setModel(self.playlistModel)
        self.playlistTableView.verticalHeader().setVisible(False)
        self.playlistTableView.horizontalHeader().setStretchLastSection(True)
        # Hide the song ID column
        self.playlistTableView.hideColumn(PlaylistModel.SONG_ID_COL)
        # If we are not in performer mode, hide the performer column
        if not self.settings.performerMode:
            self.playlistTableView.hideColumn(PlaylistModel.PERF_COL)
        # Remove songs when "del" key is pressed
        self.playlistTableView.removeSongs.connect(self.removeFromPlaylist)
        # Use a custom context menu
        self.playlistTableView.customContextMenuRequested.connect(
            self.showPlaylistContextMenu)

        # Setup buttons
        self.playButton.clicked.connect(self.play)
        self.stopButton.clicked.connect(self.stop)
        self.nextButton.clicked.connect(self.next)

        # Setup toolbar and menu
        self.actionMenuNewScreen.triggered.connect(self.showNewLyricsWindow)
        self.actionNewScreen.triggered.connect(self.showNewLyricsWindow)
        self.actionMenuSettings.triggered.connect(self.showSettings)
        self.actionToggleServer.triggered.connect(self.toggleServer)

        # CdgPlayer
        self.cdgPlayer = CdgPlayer()
        # Play next song (if there is one) when we reach the end of the
        # current song
        self.cdgPlayer.endOfMedia.connect(self.next)

        # KaraokeServer
        self.karaokeServer = KaraokeServer (self.songbookJSON,
                                            self.settings.adminPassword)
        self.karaokeServerState = KaraokeServer.OFF
        # Set up a QLabel on the toolbar. We will replace the text of the label
        # whenever we toggle the server's state.
        # NOTE: This needs ot be setup before we try to start the server
        self.toggleServerLabel = self.toolBar.addWidget(QtWidgets.QLabel())
        self.serverOnIcon = QtGui.QIcon()
        self.serverOnIcon.addPixmap(QtGui.QPixmap("images/start_server.png"),
                                     QtGui.QIcon.Normal,
                                     QtGui.QIcon.Off)
        self.serverOffIcon = QtGui.QIcon()
        self.serverOffIcon.addPixmap(QtGui.QPixmap("images/stop_server.png"),
                                    QtGui.QIcon.Normal,
                                    QtGui.QIcon.Off)
        # We need to connect the serverStateChanged signal before trying to
        # start the server.
        self.karaokeServer.serverStateChanged.connect(
            self.processServerStateChanged)

        if self.settings.serverOnStartup:
            result = self.karaokeServer.startServer(
                QtNetwork.QHostAddress(self.settings.hostAddress),
                self.settings.hostPort)
            if not result:
                alert = AlertDialog("Karaoke Server Error", "Could not start "
                                                            "Karaoke Server "
                                                            "on %s:%d" %
                                    (self.settings.hostAddress,
                                    self.settings.hostPort))
                alert.exec()
                # If we fail to connect on startup, set the server toggle
                # icon to serverOffIcon
                self.processServerStateChanged(KaraokeServer.OFF)

        self.karaokeServer.addToPlaylist.connect(self.appendToPlaylist)
        self.karaokeServer.play.connect(self.play)
        self.karaokeServer.nextSong.connect(self.next)
        self.karaokeServer.stop.connect(self.stop)
        self.karaokeServer.playNow.connect(self.insertInPlaylistAt)
        self.karaokeServer.playNext.connect(self.insertInPlaylistAt)

        self.songbookUpdated.connect(self.karaokeServer.updateSongbook)
        self.playlistModel.playlistUpdated.connect(
            self.karaokeServer.updatePlaylist)


        # Number of active lyrics windows being displayed
        self.numLyricsWindows = 0


    ###### Slots
    @QtCore.pyqtSlot()
    def play(self):
        song = self.playlistModel.getCurSong()
        self._playSong(song)


    @QtCore.pyqtSlot()
    def next(self):
        nextSong = self.playlistModel.getNextSong()
        self._playSong(nextSong)


    def _playSong (self, song):
        self.stop()
        if song:
            songName = song[PlaylistModel.SONG_NAME]
            songID = song[PlaylistModel.SONG_ID]
            # Get mp3 filepath and cdg filepath from the database
            query = QtSql.QSqlQuery()
            query.exec('SELECT mp3FilePath, cdgFilePath from songs where '
                       'songID = %d' % songID)
            # retrieve the result and play the song
            if query.first():
                isPlaying = self.cdgPlayer.play(query.value(0), query.value(1))
            else:
                alert = AlertDialog("Song Not Found",
                                    'Could not play "%s"' %
                                    songName)
                alert.exec()
                # Remove the song from the list
                self.playlistModel.removeSong(0)
                return

            if isPlaying:
                # If there are no lyrics windows being displayed, open one
                if self.numLyricsWindows < 1:
                    self.showNewLyricsWindow()


    @QtCore.pyqtSlot()
    def stop(self):
        self.cdgPlayer.stop()


    @QtCore.pyqtSlot()
    def playNow(self):
        result = self._insertSongAt(0)
        if result:
            self.stop()
            self.play()


    @QtCore.pyqtSlot()
    def playNext(self):
        self._insertSongAt(1)


    @QtCore.pyqtSlot()
    def addToPlaylist(self):
        selectedSongs = []
        performer = ""

        rows = self.searchResultsTableView.selectionModel().selectedRows()
        for modelIndex in rows:
            songName = (self.sortFilterProxyModel.index(modelIndex.row(),
                                                        self.ARTIST_COL).data()
                        + ' - '
                        + self.sortFilterProxyModel.index(modelIndex.row(),
                                                          self.TITLE_COL).data())
            songID = self.sortFilterProxyModel.index(modelIndex.row(),
                                                     self.SONG_ID_COL).data()
            selectedSongs.append([songName, songID])

        if self.settings.performerMode:
            (result, performer) = self._confirmAddToPlaylist(selectedSongs)

        if not self.settings.performerMode or result:
            selectedSongs = [[performer] + selectedSong for selectedSong in
                             selectedSongs]
            self.appendToPlaylist(selectedSongs)


    @QtCore.pyqtSlot(list)
    def appendToPlaylist(self, songs):
        self.playlistModel.appendSongs(songs)
        self.playlistTableView.resizeColumnsToContents()


    @QtCore.pyqtSlot(list, int)
    def insertInPlaylistAt(self, song, position):
        self.playlistModel.insertSongs(position, song)
        self.playlistTableView.resizeColumnsToContents()


    def _insertSongAt(self, position):
        performer = ""
        songInfo = self._getSearchResultsSelection()
        if songInfo:
            songName = songInfo[self.ARTIST_COL] \
                       + ' - ' \
                       + songInfo[self.TITLE_COL]
            songID = songInfo[self.SONG_ID_COL]
            selectedSong = [[songName, songID]]
            if self.settings.performerMode:
                (result, performer) = self._confirmAddToPlaylist(selectedSong)

            if not self.settings.performerMode or result:
                selectedSong = [[performer] + selectedSong[0]]
                self.insertInPlaylistAt(selectedSong, position)
                return True
        return False


    def _getSearchResultsSelection(self):
        modelIndex = self.searchResultsTableView.selectionModel().currentIndex()
        if modelIndex:
            return (self.sortFilterProxyModel.index
                    (modelIndex.row(), self.ARTIST_COL).data(),
                    self.sortFilterProxyModel.index
                    (modelIndex.row(), self.TITLE_COL).data(),
                    self.sortFilterProxyModel.index
                    (modelIndex.row(), self.SONG_ID_COL).data())
        else:
            return None


    def _confirmAddToPlaylist(self, selectedSongs):
        performer = ""
        addToPlaylistDialog = \
            AddToPlaylistDialog([selectedSong[0] for selectedSong in
                                 selectedSongs],
                                self.settings.defaultPerformerName,
                                self.settings.alwaysUsePerformersName,
                                self)
        result = addToPlaylistDialog.exec()
        if result:
            performer = addToPlaylistDialog.performerNameLineEdit.text()
            self.settings.alwaysUsePerformersName = \
                addToPlaylistDialog.alwaysUseNameCheckbox.isChecked()
            if self.settings.alwaysUsePerformersName:
                self.settings.defaultPerformerName = \
                    addToPlaylistDialog.performerNameLineEdit.text()
            else:
                self.settings.defaultPerformerName = ""
        return (result, performer)


    @QtCore.pyqtSlot()
    def processSearch(self):
        # Grab search text and query the database for results
        text = self.searchLineEdit.text()

        query = QtSql.QSqlQuery()
        query.prepare(
            'SELECT artist, title, songID FROM songs '
            + 'WHERE LOWER(artistNoPunc) LIKE LOWER(?) '
            + 'OR LOWER(artist) like LOWER (?)'
            + 'OR LOWER(titleNoPunc) like LOWER (?)'
            + 'OR LOWER(title) like LOWER (?) '
            + 'ORDER BY artist, title COLLATE NOCASE')
        query.addBindValue('%' + text + '%')
        query.addBindValue('%' + text + '%')
        query.addBindValue('%' + text + '%')
        query.addBindValue('%' + text + '%')
        query.exec_()
        self.sqlQueryModel.setQuery(query)

        # QSqlQueryModel only fetches 256 rows at a time
        # Keep fetching until all rows are fetched
        while (self.sqlQueryModel.canFetchMore()):
            self.sqlQueryModel.fetchMore()

        self.searchResultsTableView.hideColumn(self.SONG_ID_COL)


    @QtCore.pyqtSlot()
    def startKeypressTimer(self):
        # Stop the timer
        # If it is still active, this means that the user has not finished
        # typing
        self.__keypressTimer.stop()
        # Start the timer for 250 ms
        self.__keypressTimer.start(250)


    @QtCore.pyqtSlot()
    def showNewLyricsWindow(self):
        lyricsWindow = LyricsWindow(self.cdgPlayer, self)
        lyricsWindow.closedWindow.connect(self.closeLyricsWindow)
        lyricsWindow.show()
        self.numLyricsWindows += 1


    @QtCore.pyqtSlot()
    def closeLyricsWindow(self):
        self.numLyricsWindows -= 1
        # if there are no more lyrics windows, then stop playback
        if self.numLyricsWindows < 1:
            self.stop()


    @QtCore.pyqtSlot()
    def toggleServer(self):
        if self.karaokeServerState == KaraokeServer.ON:
            self.karaokeServer.stopServer()
        else:
            print (self.settings.hostPort)
            result = self.karaokeServer.startServer(
                QtNetwork.QHostAddress(self.settings.hostAddress),
                self.settings.hostPort)
            if not result:
                alert = AlertDialog("Karaoke Server Error", "Could not start "
                                                            "Karaoke Server "
                                                            "on %s:%d" %
                                    (self.settings.hostAddress,
                                     self.settings.hostPort))
                alert.exec()


    @QtCore.pyqtSlot(int)
    def processServerStateChanged(self, state):
        self.karaokeServerState = state
        label = self.toolBar.widgetForAction(self.toggleServerLabel)
        if state == KaraokeServer.ON:
            self.actionToggleServer.setIcon(self.serverOffIcon)
            label.setText("Serving: %s:%d" % (self.settings.hostAddress,
                                              self.settings.hostPort))
            self.actionToggleServer.setToolTip("Turn server off")
        else:
            self.actionToggleServer.setIcon(self.serverOnIcon)
            label.setText("Not Serving")
            self.actionToggleServer.setToolTip("Turn server on")


    @QtCore.pyqtSlot()
    def showSettings(self):
        settingsDialog = SettingsDialog(self.settings, self)
        settingsDialog.updateDatabaseClicked.connect(self.updateDatabaseClicked)
        settingsDialog.exec()
        if settingsDialog.result():
            self._processNewSettings(settingsDialog.getSettings())


    @QtCore.pyqtSlot(list)
    def updateDatabaseClicked(self, searchFolders):
        # On update database click, update our searchFolders setting with the
        # new folders and write out the settings to the ini file
        self._createSongbook(searchFolders)
        self.sqlQueryModel.setQuery \
            ('SELECT artist, title, songID from songs')
        # QSqlQueryModel only fetches 256 rows at a time
        # Keep fetching until all rows are fetched
        while (self.sqlQueryModel.canFetchMore()):
            self.sqlQueryModel.fetchMore()

        self.settings.searchFolders = searchFolders
        Settings.writeSettings(self.settings, self.SETTINGS_FILE)
        self.karaokeServer.setSongbook(self.songbookJSON)


    def _processNewSettings (self, newSettings):
        if newSettings.performerMode != self.settings.performerMode:
            # Toggle back to non performer mode
            if self.settings.performerMode:
                self.playlistTableView.hideColumn(PlaylistModel.PERF_COL)
            else: # Toggle to performer mode
                self.playlistTableView.showColumn(PlaylistModel.PERF_COL)

        if newSettings.adminPassword != self.settings.adminPassword:
            self.karaokeServer.updatePassword(newSettings.adminPassword)

        if set(newSettings.searchFolders) != set (self.settings.searchFolders):
            self._createSongbook(newSettings.searchFolders)
            self.sqlQueryModel.setQuery \
                ('SELECT artist, title, songID from songs')
            # QSqlQueryModel only fetches 256 rows at a time
            # Keep fetching until all rows are fetched
            while (self.sqlQueryModel.canFetchMore()):
                self.sqlQueryModel.fetchMore()

        self.settings = newSettings
        # Write out new settings
        Settings.writeSettings(self.settings, self.SETTINGS_FILE)


    @QtCore.pyqtSlot(QtCore.QPoint)
    def showSearchResultsContextMenu(self, position):
        menu = QtWidgets.QMenu(self)
        playNowAct = QtWidgets.QAction("Play now", self)
        playNowAct.triggered.connect(self.playNow)
        menu.addAction(playNowAct)

        playNextAct = QtWidgets.QAction("Play next", self)
        playNextAct.triggered.connect(self.playNext)
        menu.addAction(playNextAct)

        separatorAct = QtWidgets.QAction(self)
        separatorAct.setSeparator(True)
        menu.addAction(separatorAct);

        addToPlaylistAct = QtWidgets.QAction("Add to playlist", self)
        addToPlaylistAct.triggered.connect(self.addToPlaylist)
        menu.addAction(addToPlaylistAct)

        # Place menu where the cursor is
        menu.exec(self.searchResultsTableView.mapToGlobal(position))


    @QtCore.pyqtSlot(QtCore.QPoint)
    def showPlaylistContextMenu(self, position):
        menu = QtWidgets.QMenu(self)
        removeFromPlaylistAction = QtWidgets.QAction\
            ("Remove from playlist", self)
        removeFromPlaylistAction.triggered.connect(self.removeFromPlaylist)
        menu.addAction(removeFromPlaylistAction)
        # Place menu where the cursor is
        menu.exec(self.playlistTableView.mapToGlobal(position))


    @QtCore.pyqtSlot()
    def removeFromPlaylist(self):
        rows = self.playlistTableView.selectionModel().selectedRows()
        numRemoved = 0

        # We remove songs in ascending order because with each song removed
        # the index of the next song to remove decrements by 1
        rows.sort()
        for modelIndex in rows:
            self.playlistModel.removeSong(modelIndex.row() - numRemoved)
            numRemoved += 1


    def _createSongbook (self, searchFolders):
        # Convert to a set to remove any redundant folders
        searchFolders = set(searchFolders)

        self.songbookdb.exec("DROP TABLE songs")
        self.songbookdb.exec(
                "CREATE TABLE songs(artist TEXT, artistNoPunc TEXT, "
                "title TEXT, titleNoPunc TEXT, "
                "mp3FilePath TEXT, cdgFilePath TEXT, "
                "songID INTEGER PRIMARY KEY AUTOINCREMENT)")

        # Create the songbook JSON file
        # The file will have the following structure:
        # {"response": "getsongbook""data": [{"artist": artist, "title": title,
        # "artistNoPunc":
        #            artistNoPunc, "titleNoPunc": titleNoPunc, "songID": id},...
        #           ]}
        self.songbookJSON = []

        # We scan through the folders and store mp3 files we find in the
        # mp3Files dictionary as
        # {mp3_lowercase_filepath_no_ext : mp3_filepath} and
        # cdg files we find in the cdgFiles dictionary as
        # {cdg_lowercase_filepath_no_ext : cdg_filepath}.
        # We then go through each mp3 file entry in mp3Files and check to see
        # if it is in cdgFiles. If it is, we insert that pair in our
        # songbook database. If there is no match for the mp3 file, we store
        # its file path in unmatchedSongs which will be written to a log
        # file in the end. After all mp3_files are checked, we check cdgFiles
        # for any cdgFiles which were never matched and write those files to
        # unmatchedSongs.
        # Note, we use the whole filepath as the key because that uniquely
        # identifies a song.
        mp3Files = {}
        cdgFiles = {}
        unmatchedSongs = []


        for searchFolder in searchFolders:
            for path, dirs, filenames in os.walk(searchFolder):
                for file in filenames:
                    # Get filename and extension
                    name, ext = os.path.splitext(file)

                    # Get filepath in lower case without extension to use as a
                    # key. We use the lower case filepath as the key because
                    # in Windows, filenames are case insensitive.
                    # Therefore we can have cases where "foo.mp3" should match
                    # with "FOO.cdg.
                    lowerCaseFilepath = (path.replace ('\\','/') + '/'
                                           + name).lower()
                    filepath = path.replace('\\', '/') + '/' + file

                    if ext.lower() == '.mp3':
                        mp3Files[lowerCaseFilepath] = filepath
                    elif ext.lower() == '.cdg':
                        cdgFiles[lowerCaseFilepath] = filepath

        # Count total mp3 and cdg files found. If there are files to process
        # (i.e. totalFiles > 0), display a QProgressDialog and process the
        # the files.
        totalFiles = len(mp3Files) + len(cdgFiles)
        if totalFiles > 0:
            progressDialog = QtWidgets.QProgressDialog(self,
                                                       QtCore.Qt.WindowTitleHint
                                                       | QtCore.Qt.
                                                       WindowCloseButtonHint)
            progressDialog.setWindowTitle("Loading Songs")
            # Only show the progressDialog if 2000ms has passed
            progressDialog.setMinimumDuration(2000)
            progressDialog.setWindowModality(QtCore.Qt.WindowModal)
            progressDialog.setCancelButton(None)
            progressDialog.setRange(0, totalFiles)

            # Start a database transaction. We only want to commit the
            # database inserts as a batch rather than one at a time.
            self.songbookdb.transaction()
            i = 0
            while i < (totalFiles):
                # If there are mp3_files, process them first.
                if len(mp3Files):
                    fileKey, mp3FilePath = mp3Files.popitem()
                    # Check if filename exists in cdg_files. If it does,
                    # add the song to the database.
                    cdgFilePath = cdgFiles.get(fileKey)
                    if cdgFilePath:
                        # We arbitrarily use the mp3FilePath filename as the
                        # text we parse for "artist" and "title" entries. We
                        # don't use file_key because it was converted into
                        # lower case.
                        artistTitle = os.path.splitext(os.path.basename (
                            os.path.normpath(mp3FilePath)))[0]
                        self._addSongToDB(artistTitle, mp3FilePath,
                                         cdgFilePath)

                        # Remove the cdg file from cdg_files and increment "i"
                        # 2 to update the progress bar.
                        del cdgFiles[fileKey]
                        i += 2
                    else: # Could not find a cdg match for the mp3 file
                        unmatchedSongs.append(mp3FilePath)
                        i += 1
                elif len (cdgFiles): # Process leftover cdg files
                    fileKey, cdgFilePath = cdgFiles.popitem()
                    unmatchedSongs.append(cdgFilePath)
                    i += 1

                progressDialog.setValue(i)
                progressDialog.setLabelText\
                    ("Processing file number %d of %d" % (i, totalFiles))
                QtCore.QCoreApplication.processEvents()
            # Once all song insertions have been executed, commit the
            # transactions and close the database.
            self.songbookdb.commit()

            self.songbookJSON = {"cmd": "getSongbook",
                                 "response": {"data": self.songbookJSON}}
            self.songbookJSON = json.dumps(self.songbookJSON)
            f = open(self.SONGBOOK_JSON_FILE, 'w')
            f.write(self.songbookJSON)
            f.close()

            # If there are unmatched songs, write them out to a log file so
            # the user can fix them.
            if unmatchedSongs:
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                # Try to create a logs directory if one does not exist
                if not os.path.isdir('logs'):
                    os.makedirs('logs')
                try:
                    f = open(
                        'logs/unmatched_song_files_' + timestamp + '.log',
                        'w')
                    unmatchedSongs.sort()
                    for song in unmatchedSongs:
                        f.write ('%s\n' % song)
                    f.close()
                except:
                    return
            self.songbookUpdated.emit(self.songbookJSON)


    def _addSongToDB (self, artistTitle, mp3FilePath, cdgFilePath):
        (artist, artistNoPunc, title, titleNoPunc) = \
            self._parseSongName(artistTitle)

        query = QtSql.QSqlQuery()
        query.prepare(
            'INSERT INTO songs (artist, artistNoPunc, '
            'title, titleNoPunc, mp3FilePath, cdgFilePath)'
            ' VALUES (?, ?, ?, ?, ?, ?)')
        query.addBindValue(artist)
        query.addBindValue(artistNoPunc)
        query.addBindValue(title)
        query.addBindValue(titleNoPunc)
        query.addBindValue(mp3FilePath)
        query.addBindValue(cdgFilePath)
        query.exec_()

        query.exec('SELECT max(songID) FROM songs')
        query.first()
        lastRowID = query.value(0)

        # Add the song to songbookJSON
        self.songbookJSON.append(collections.OrderedDict(
            {"artist": artist,
             "title": title,
             "artistNoPunc": artistNoPunc,
             "titleNoPunc": titleNoPunc,
             "songID": lastRowID}))

    def _parseSongName(self, artistTitle):
        # Separate artist and title from the filename. We assume a hyphen
        # separates the two.
        splitPattern = "(.+)\s+-\s+(.+)"
        m = re.match(splitPattern, artistTitle)
        if m:  # If there is a match
            artist = m.group(1)
            title = m.group(2)
        else:
            artist = "Unknown"
            title = artistTitle

        # Create "no punctuation" versions of artistTitle
        puncPattern = "['|,|.|(|)|-]"
        artistNoPunc = re.sub(puncPattern, "", artist)
        titleNoPunc = re.sub(puncPattern, "", title)

        return (artist, artistNoPunc, title, titleNoPunc)


    def closeEvent(self, event):
        # Close the database
        self.songbookdb.close()


def main():
    app = QtWidgets.QApplication(sys.argv)
    pyks = PyKS()
    pyks.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
