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
import re

HTTP_VERSION_REGEX = re.compile("HTTP/\d+.\d+")

class HTTPMessage (object):
    REQUEST_TYPE = 1
    RESPONSE_TYPE = 2

    def __init__(self):
        self._messageType = HTTPMessage.REQUEST_TYPE

        # Request specific start line fields
        self._method = ""
        self._requestUri = ""

        # Response specific start line fields
        self._statusCode = ""
        self._statusPhrase = ""

        self._httpVer = ""
        self._headerFields = {}
        self._body = ""

    def setMethod(self, method):
        self._method = method

    def setRequestURI (self, requestURI):
        self._requestURI = requestURI

    def setStatusCode (self, statusCode):
        self._statusCode = statusCode

    def set_statusPhrase (self, statusPhrase):
        self._statusPhrase = statusPhrase

    def setHTTPVersion (self, httpVer):
        self._httpVer = httpVer

    def addHeaderField (self, fieldName, fieldValue):
        self._headerFields[fieldName] = fieldValue

    def getMethod(self):
        return self._method

    def getRequestURI (self):
        return self._requestURI

    def getStatusCode (self):
        return self._statusCode

    def getStatusPhrase (self):
        return self._statusPhrase

    def getHTTPVersion (self):
        return self._httpVer

    def hasHeaderField (self, fieldName):
        return fieldName in self._headerFields.keys()

    def getFieldValue (self, fieldName):
        if self.hasHeaderField(fieldName):
            return self._headerFields[fieldName]
        else:
            return None

    def __str__(self):
        msg = ''
        if self._messageType == HTTPMessage.REQUEST_TYPE:
            msg += 'Method: ' + self._method + '\n'
            msg += 'request_uri: ' + self._requestURI + '\n'
            msg += "HTTP Ver: " + self._httpVer + '\n'
        else:
            msg += 'HTTP Ver: ' + self._httpVer + '\n'
            msg += 'Status Code: ' + self._statusCode + '\n'
            msg += 'Status Phrase: ' + self._statusPhrase + '\n'

        for header_field, header_value in self._headerFields.items():
            msg += header_field + ': ' + header_value + '\n'
        return msg

class SimpleHTTPParser (object):

    @staticmethod
    def parse (data):

        message = HTTPMessage()

        # Find the message header
        # It will end in CRLFCRLF (i.e. \r\n\r\n)
        idx = data.find ('\r\n\r\n')

        # If '\r\n\r\n' is not found, this is a mangled HTTP message
        if idx < 0:
            return None

        messageHeader = data[:idx]
        messageBody = data[idx + 4:]

        # Parse the start line to determine the method,
        # request URI and HTTP version
        idx = messageHeader.find('\r\n')

        startLine = messageHeader[:idx]
        headerFields = messageHeader[idx + 2:]

        startLine = startLine.split()

        # A start line consists of three parts
        # For Requests:
        #    Method
        #    Request URI
        #    HTTP Version
        # For Responses:
        #    HTTP Version
        #    Status Code
        #    Reason Phrase
        # If this message's status line does not contain 3 components
        # it is mangled.
        if len (startLine) ==  3:
            # Determine if the message is a request or response
            # by determining if the first part of the message is
            # an HTTP version. If it is then this message is a
            # response message. Otherwise, it is a request message.
            if HTTP_VERSION_REGEX.match (startLine[0]):
                message.setHTTPVersion(startLine[0])
                message.setStatusCode(startLine[1])
                message.setStatusPhrase(startLine[2])
            else:
                message.setMethod(startLine[0])
                message.setRequestURI (startLine[1])
                message.setHTTPVersion(startLine[2])

            # Grab the header fields
            headerFields = headerFields.split('\r\n')
            for headerField in headerFields:
                headerField = headerField.split (':', 1)
                # Make sure there is a field name and value
                if len (headerField) == 2:
                    message.addHeaderField(headerField[0].strip().lower(),
                                             headerField[1].strip())
                else: # A header field was mangled
                    return None
            return message
        else: # Start line did not consist of three parts
            return None
