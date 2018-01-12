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
from PyQt5 import QtCore, QtNetwork, QtWebSockets

# Python3 std lib imports
import collections
import json
import os
import time

# PyKS imports
from http_utils import SimpleHTTPParser

class WebServer (QtCore.QObject):

    EXTENSION_TO_MIME_TYPE = {'.css': b'text/css',
                              '.html': b'text/html',
                              '.htm': b'text/html',
                              '.js': b'text/javascript',
                              '.txt': b'text/plain',
                              '.xml': b'text/xml',
                              '.ico': b'images/png',
                              '.woff2': b'font/woff2',
                              '.png': b'images/png'
                              }
    FIRST_PAGE = '/index.html'
    ROOT_DIR = 'www'

    WebResource = collections.namedtuple(
        'WebResource', ['data', 'size', 'mime_type'])

    def __init__(self, parent=None):
        super (WebServer, self).__init__(parent)

        self.HTTPMethods = {'GET': self._processGET}
        self.webResources = {}
        self.tcpServer = QtNetwork.QTcpServer(self)

    def startServer(self, hostAddress, hostPort):
        # Read all the files we will be serving into memory
        for root, dirs, files in os.walk('www'):
            for file in files:
                filePath = os.path.join(root, file)
                mime_type = self.EXTENSION_TO_MIME_TYPE.get(
                    os.path.splitext(filePath)[1].lower(), 'text/plain')
                f = open(filePath, 'rb')
                uri = filePath.replace(os.path.sep, '/').replace(
                    self.ROOT_DIR, '')
                self.webResources[uri] = (self.WebResource(f.read(),
                                                           os.path.getsize(
                                                               filePath),
                                                           mime_type))
                # Add FIRST_PAGE
                if uri == self.FIRST_PAGE:
                    f.seek(0)
                    self.webResources['/'] = (
                        self.WebResource(f.read(), os.path.getsize(filePath),
                                         mime_type))
                f.close()

        # Start the server
        if not self.tcpServer.listen(hostAddress, hostPort):
            return False
        self.tcpServer.newConnection.connect(self.processNewConnection)
        return True


    def stopServer(self):
        self.tcpServer.close()


    def addResource(self, resourceName, resourceData):
        mime_type = self.EXTENSION_TO_MIME_TYPE.get(
            os.path.splitext(resourceName)[1].lower(), 'text/plain')
        if resourceName[0] != '/':
            resourceName = '/' + resourceName
        self.webResources[resourceName] = \
            self.WebResource(resourceData, len(resourceData), mime_type)
        # Also add it as FIRST_PAGE resourceName matches
        if resourceName == self.FIRST_PAGE:
            self.webResources['/'] = \
                self.WebResource(resourceData, len(resourceData), mime_type)


    @QtCore.pyqtSlot()
    def processNewConnection(self):
        while (self.tcpServer.hasPendingConnections()):
            socket = self.tcpServer.nextPendingConnection()
            socket.readyRead.connect(self.processReadyRead)


    @QtCore.pyqtSlot()
    def processReadyRead(self):
        socket = self.sender()
        message = SimpleHTTPParser.parse(str (socket.readAll(),
                                              encoding='UTF-8'))
        if message:
            method = message.getMethod()
            if method in self.HTTPMethods:
                self.HTTPMethods[method](message)


    def _processGET(self, message):
        socket = self.sender()
        requestURI = message.getRequestURI()

        date = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime()).\
            encode('ascii')
        if requestURI in self.webResources:
            status = b'200 OK'
            webResource = self.webResources[requestURI]
        else:
            status = b'404 Not Found'
            webResource = self.webResources['/notfound.html']

        data = (b''
                b'HTTP/1.1 %s\r\n'
                b'CONTENT-LENGTH: %d\r\n'
                b'CONTENT-TYPE: %s\r\n'
                b'DATE: %s\r\n\r\n'
                b'%s') % (
               status, webResource.size, webResource.mime_type,
               date, webResource.data)
        socket.write(data)


class KaraokeServer(QtCore.QObject):
    addToPlaylist = QtCore.pyqtSignal(list)
    play = QtCore.pyqtSignal()
    nextSong = QtCore.pyqtSignal()
    stop = QtCore.pyqtSignal()
    playNow = QtCore.pyqtSignal(list, int)
    playNext = QtCore.pyqtSignal(list, int)
    serverStateChanged = QtCore.pyqtSignal(int)

    WEB_APP_PATH = os.path.join (os.path.dirname(__file__), 'www/index.html')

    PERFORMER = 0
    SONG_NAME = 1
    SONG_ID = 2

    OFF = 0
    ON = 1

    def __init__(self, songbook="", parent=None):
        super (KaraokeServer, self).__init__(parent)

        self.songbook = songbook

        self.password = ""
        self.playlist = []

        self.maxConnectedClients = 0

        # The KaraokeServer consists of a WebSocketServer and a WebServer.
        self.webSocketServer = QtWebSockets.QWebSocketServer(
            "Karaoke Server", QtWebSockets.QWebSocketServer.NonSecureMode, self)
        self.webSocketServerPort = 0;
        self.WebSocketMethods = {'getSongbook': self._getSongbook,
                                 'getPlaylist':self._getPlaylist,
                                 'updatePlaylist':self._updatePlaylist,
                                 'addToPlaylist': self._addToPlaylist,
                                 'play': self._play,
                                 'nextSong': self._nextSong,
                                 'stop': self._stop,
                                 'playNow': self._playNow,
                                 'playNext': self._playNext,
                                 'submitPassword' : self._submitPassword
                                 }

        self.webServer = WebServer()

        # Clients hold all clients connected to the WebSocketServer. Clients
        # are added when they connect and removed when they disconnect.
        # Admins holds IPs of clients who have administrative privileges.
        self.clients = {}
        self.admins = set()

    def startServer(self, hostAddress, hostPort, maxConnectedClients,
                    allowMultipleConnections, password):
        # If this is the first time we are starting the server (i.e. PyKS just
        # launched), then self.webSocketServerPort will be set to 0 indicating
        # that we should be assigned a port. Once a port is assigned, set
        # self.webSocketServerPort to that port so that on subsequent
        # startServer calls, we use the same webSocketServer port. This will
        # allow clients to reconnect (i.e. they cannot reconnect if the server
        # runs on a new port every time it starts).
        if not self.webSocketServer.listen(hostAddress,
                                           self.webSocketServerPort):
            return False
        self.webSocketServerPort = self.webSocketServer.serverPort()

        self.webSocketServer.newConnection.connect(self.processNewConnection)

        if not self.webServer.startServer(hostAddress, hostPort):
            return False
        webAppName = os.path.basename(self.WEB_APP_PATH)
        try:
            f = open (self.WEB_APP_PATH)
            webAppData = f.read()
        except:
            self.webSocketServer.close()
            self.webServer.stopServer()
            return False
        webAppData = webAppData.replace('{hostAddressPort}',
                               hostAddress.toString()
                               + ':'
                               + str(self.webSocketServer.serverPort()))
        self.webServer.addResource(webAppName, bytes(webAppData, 'UTF-8'))
        self.serverStateChanged.emit(self.ON)
        f.close()

        # Save server settings
        self.maxConnectedClients = maxConnectedClients
        self.allowMultipleConnections = allowMultipleConnections
        self.password = password
        return True


    def stopServer(self):
        # Clear admins and clients
        self.clients.clear()
        self.admins.clear()

        self.webServer.stopServer()
        self.webSocketServer.close()
        self.serverStateChanged.emit(self.OFF)


    @QtCore.pyqtSlot(list)
    def updatePlaylist(self, playlist):
        self.playlist = playlist
        # Update clients
        response = self._createPlaylistResponse("updatePlaylist")
        for socketKey, client in self.clients.items():
            client.sendTextMessage(response)


    @QtCore.pyqtSlot('QString')
    def updateSongbook(self, songbook):
        self.songbook = songbook


    @QtCore.pyqtSlot()
    def processNewConnection(self):
        while (self.webSocketServer.hasPendingConnections()):
            socket = self.webSocketServer.nextPendingConnection()
            if (self.maxConnectedClients < 0
                or len(self.clients) < self.maxConnectedClients):
                socket.textMessageReceived.connect(self.processTextMessage)
                socket.disconnected.connect(self.processClientDisconnect)

                if self.allowMultipleConnections:
                    # If we allow multiple connections from the same client,
                    # we use the IP address concatenated with the port as the
                    #  socket key becuase a client can connect to the server
                    # through different browsers/browser tabs. Otherwise,
                    # we just use the IP address and don't allow the
                    # connection if a connection with the client already
                    # exists.
                    socketKey = socket.peerAddress().toString() \
                                + ":" \
                                + str(socket.peerPort())
                else:
                    socketKey = socket.peerAddress().toString()
                if not socketKey in self.clients:
                    self.clients[socketKey] = socket
                else:
                    socket.close(4000, # Close code
                        "Only a single connection to the server is allowed!")
            else:
                # Close the socket with an error message
                socket.close(4001, # Close code
                             "Server is no longer allowing new connections!")


    @QtCore.pyqtSlot()
    def processClientDisconnect(self):
        socket = self.sender()
        if self.allowMultipleConnections:
            socketKey = socket.peerAddress().toString() \
                    + ":" \
                    + str(socket.peerPort())
        else:
            socketKey = socket.peerAddress().toString()
        if socketKey in self.clients:
            if socket == self.clients[socketKey]:
                del self.clients[socketKey]
        if socketKey in self.admins:
            self.admins.remove(socketKey)


    @QtCore.pyqtSlot('QString')
    def processTextMessage(self, message):
        message = json.loads(message)
        if len(message) == 1:
            cmd, args = message.popitem()
            if cmd in self.WebSocketMethods:
                self.WebSocketMethods[cmd](args)


    def _getSongbook(self, args):
        socket = self.sender()
        socket.sendTextMessage(self.songbook)


    def _getPlaylist(self, args):
        socket = self.sender()
        response = self._createPlaylistResponse("getPlaylist")
        socket.sendTextMessage(response)


    def _updatePlaylist(self, args):
        socket = self.sender()
        response = self._createPlaylistResponse("updatePlaylist")
        socket.sendTextMessage(response)


    def _createPlaylistResponse(self, cmd):
        response = {"cmd": cmd, "response": {"data":[]}}
        curPlaylist = []
        if self.playlist:
            for song in self.playlist:
                curPlaylist.append({"performer": song[self.PERFORMER],
                                    "song": song[self.SONG_NAME]})

            response["response"]["data"] = curPlaylist
        return json.dumps(response)


    def _addToPlaylist(self, args):
        socket = self.sender()
        # args is a list with the following items
        # [performer, artist - title, song ID]
        self.addToPlaylist.emit([args])

        # Send response acknowledging receipt of song request
        response = {"cmd": "addToPlaylist", "response": args[1]}
        socket.sendTextMessage(json.dumps(response))


    def _submitPassword(self, args):
        socket = self.sender()
        response = {"cmd": "submitPassword", "response": False}
        if len(args) == 1:
            if args[0] == self.password:
                # Add client to the admin list
                socketKey = socket.peerAddress().toString() \
                            + ":" \
                            + str(socket.peerPort())
                self.admins.add(socketKey)
                response["response"] = True
        socket.sendTextMessage(json.dumps(response))


    def _verifyClient(self, socket):
        socketKey = socket.peerAddress().toString() \
                    + ":" \
                    + str(socket.peerPort())
        if socketKey in self.admins:
            return True
        return False


    def _play(self, args):
        socket = self.sender()
        # Check if client is in admins
        if self._verifyClient(socket):
            self.play.emit()


    def _nextSong(self, args):
        socket = self.sender()
        # Check if client is in admins
        if self._verifyClient(socket):
            self.nextSong.emit()


    def _stop(self, args):
        socket = self.sender()
        # Check if client is in admins
        if self._verifyClient(socket):
            self.stop.emit()


    def _playNow(self, args):
        socket = self.sender()
        if self._verifyClient(socket):
            self.playNow.emit([args], 0)
        self.play.emit()


    def _playNext(self, args):
        socket = self.sender()
        if self._verifyClient(socket):
            self.playNow.emit([args], 1)
