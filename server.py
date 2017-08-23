# PyQt5 imports
from PyQt5 import QtCore, QtNetwork, QtWebSockets, QtWidgets #REMOVE WIDGETS

# Python3 std lib imports
import collections
import json
import os
import sys #REMOE
import time

from http_utils import SimpleHTTPParser

class WebServer (QtCore.QObject):

    EXTENSION_TO_MIME_TYPE = {'.css': b'text/css',
                              '.html': b'text/html',
                              '.htm': b'text/html',
                              '.js': b'text/javascript',
                              '.txt': b'text/plain',
                              '.xml': b'text/xml',
                              '.ico': b'images/png'
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
        # Read into memory all the files we will be serving into memory
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
        print (requestURI)
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

    WEB_APP_PATH = 'www/index.html'

    PERFORMER = 0
    SONG_NAME = 1
    SONG_ID = 2

    OFF = 0
    ON = 1

    def __init__(self, songbook="", password="", parent=None):
        super (KaraokeServer, self).__init__(parent)

        self.songbook = songbook
        self.password = password
        self.playlist = []

        # The KaraokeServer consists of a WebSocketServer and a WebServer.
        self.webSocketServer = QtWebSockets.QWebSocketServer(
            "Karaoke Server", QtWebSockets.QWebSocketServer.NonSecureMode, self)
        self.WebSocketMethods = {"getSongbook": self._getSongbook,
                                 "getPlaylist":self._getPlaylist,
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

    def startServer(self, hostAddress, hostPort):
        # If we can't start the webSocketServer, return False
        if not self.webSocketServer.listen(hostAddress):
            return False
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
            f.close()
            return False
        webAppData = webAppData.replace('{hostAddressPort}',
                               hostAddress.toString()
                               + ':'
                               + str(self.webSocketServer.serverPort()))
        self.webServer.addResource(webAppName, bytes(webAppData, 'UTF-8'))
        self.serverStateChanged.emit(self.ON)
        f.close()
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
    def updatePassword(self, password):
        self.password = password


    @QtCore.pyqtSlot('QString')
    def updateSongbook(self, songbook):
        self.songbook = songbook


    @QtCore.pyqtSlot()
    def processNewConnection(self):
        while (self.webSocketServer.hasPendingConnections()):
            socket = self.webSocketServer.nextPendingConnection()
            socket.textMessageReceived.connect(self.processTextMessage)
            socket.disconnected.connect(self.processClientDisconnect)

            # A client can connect to the server through different browser
            # tabs, so use both the IP address and port as the key
            socketKey = socket.peerAddress().toString() \
                        + ":" \
                        + str(socket.peerPort())
            self.clients[socketKey] = socket


    @QtCore.pyqtSlot()
    def processClientDisconnect(self):
        socket = self.sender()
        socketKey = socket.peerAddress().toString() \
                    + ":" \
                    + str(socket.peerPort())
        if socketKey in self.clients:
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
        print ("_getSongbook called")
        socket = self.sender()
        socket.sendTextMessage(self.songbook)


    def _getPlaylist(self, args):
        print ("_getPlaylist called")
        socket = self.sender()
        response = self._createPlaylistResponse("getPlaylist")
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
        print (args)
        self.addToPlaylist.emit([args])


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
        print ("_playNow called")
        socket = self.sender()
        if self._verifyClient(socket):
            self.playNow.emit([args], 0)
        self.play.emit()


    def _playNext(self, args):
        print ("_playNext called")
        socket = self.sender()
        if self._verifyClient(socket):
            self.playNow.emit([args], 1)


    def _verifyClient(self, socket):
        socketKey = socket.peerAddress().toString() \
                    + ":" \
                    + str(socket.peerPort())
        if socketKey in self.admins:
            return True
        return False


    def _submitPassword(self, args):
        print (args)
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
        print (response)
        socket.sendTextMessage(json.dumps(response))


def main():
    app = QtWidgets.QApplication(sys.argv)
    server = KaraokeServer()
    if not server.startServer(QtNetwork.QHostAddress('192.168.1.2'), 80):
        print ("could not listen")
    return app.exec_()

if __name__ == '__main__':
    main()

