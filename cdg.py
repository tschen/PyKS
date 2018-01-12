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
# Special thanks to Jim Bumgardner and his paper on CD+G entitled "CD+G
# Revealed: Playing back Karaoke tracks in Software".
# Much of the text in this module was taken directly from this document.
# https://jbum.com/cdg_revealed.html

# PyQt5 imports
from PyQt5 import QtCore, QtGui, QtMultimedia

# Python3 std lib imports
import os

# Other ext libraries
import numpy

# Only the lower 6 bits of the command, instruction, and each of the bytes of
# the data field contain CD+G information. This mask is used to mask out the
# upper two bits.
CDG_MASK = 0x3F

# CD+G commands have a value of 0x9 in their lower 6 bits
CDG_COMMAND = 0x9

# CD+G instruction value constants
CDG_MEM_PRESET = 1
CDG_BORDER_PRESET = 2
CDG_TILE_BLOCK_NORM = 6
CDG_SCROLL_PRESET = 20
CDG_SCROLL_COPY = 24
CDG_DEF_TRANSPARENT_COLOR = 28
CDG_LOAD_COLOR_TBL_LO = 30
CDG_LOAD_COLOR_TBL_HI = 31
CDG_TILE_BLOCK_XOR = 38

CDG_WIDTH = 300
CDG_HEIGHT = 216

class CdgPlayer (QtCore.QObject):
    cdgImageUpdated = QtCore.pyqtSignal()
    endOfMedia = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(CdgPlayer, self).__init__(parent)

        self.__processCdgInstructions = \
            {CDG_MEM_PRESET: self._exec_mem_preset,
             CDG_BORDER_PRESET: self._exec_border_preset,
             CDG_TILE_BLOCK_NORM: self._exec_tile_block_norm,
             CDG_SCROLL_PRESET: self._exec_scroll_preset,
             CDG_SCROLL_COPY: self._exec_scroll_copy,
             CDG_DEF_TRANSPARENT_COLOR: self._exec_def_transparaent_color,
             CDG_LOAD_COLOR_TBL_LO: self._exec_load_color_tbl_lo,
             CDG_LOAD_COLOR_TBL_HI: self._exec_load_color_tbl_hi,
             CDG_TILE_BLOCK_XOR: self._exec_load_tile_block_xor}

        # CDG frames are drawn on cdgImage once they have been decoded
        self.cdgImage = QtGui.QImage(CDG_WIDTH, CDG_HEIGHT,
                                     QtGui.QImage.Format_Indexed8)
        # Set color table count to 16 colors. We need this here because when
        # we first instantiate a QImage, there is no color table associated
        # with it and it will throw an exception. Calling setColorCount
        # creates a color table and sets all color indices to (0, 0, 0).
        self.cdgImage.setColorCount(16)
        # Make the background one color
        self.cdgImage.fill(0)

        # Convert the cdgImage into a 2D array so we can manipulate pixels
        # directly
        self.cdgImageAsBitmap = self.cdgImage.bits().asarray(CDG_WIDTH *
                                                             CDG_HEIGHT)
        self.cdgImageAsBitmap = numpy.reshape (self.cdgImageAsBitmap,
                                               (CDG_HEIGHT, CDG_WIDTH))

        # We use the QtMultimedia.QMediaPlayer to play the audio
        self.mediaPlayer = QtMultimedia.QMediaPlayer(self)
        # Set the notify interval to 60 ms. Every 60 ms,
        # the positionChanged signal will be sent and decodeCdgPackets
        # will be called to process another set of CDG packets.
        self.mediaPlayer.setNotifyInterval(60)
        self.mediaPlayer.positionChanged.connect(self.decodeCdgPackets)
        self.mediaPlayer.mediaStatusChanged.connect(
            self.processMediaStatusChanged)

        # __previousReadTime helps keep track of how much time has elapsed
        # since we processed our last set of packets.
        self.__previousReadTime = 0
        # __fractionalPacketsToProcess keeps track of our rounding error when
        # processing packets.
        self.__fractionalPacketsToProcess = 0

        # This buffer will be used to hold CDG data once we read in a CDG file.
        self.cdgBuffer = []
        # currentBytePos marks which byte we are at in cdgBuffer
        self.currentBytePos = 0


    def play(self, mp3FilePath, cdgFilePath):
        # Verify the file paths are not empty and the files exist
        if (mp3FilePath
            and cdgFilePath
            and os.path.isfile(mp3FilePath)
            and os.path.isfile(cdgFilePath)):
            try:
                cdgFile = open(cdgFilePath, 'rb')
                # We read all of the cdg file into memory to speed up processing
                self.cdgBuffer = cdgFile.read()
            except: # On exception don't try to play the song
                return False

            self.currentBytePos = 0

            # Load the MP3 file
            mp3File = QtCore.QFileInfo(mp3FilePath)
            url = QtCore.QUrl.fromLocalFile(mp3File.absoluteFilePath())
            self.mediaPlayer.setMedia(QtMultimedia.QMediaContent(url))
            return True
        return False


    def stop(self):
        # Set background to solid color
        self.cdgImage.fill(0)
        # clear the mediaPlayer content
        self.mediaPlayer.setMedia(QtMultimedia.QMediaContent())
        self.mediaPlayer.stop()
        return True


    def getCdgImage(self):
        return self.cdgImage


    @QtCore.pyqtSlot(QtMultimedia.QMediaPlayer.MediaStatus)
    def processMediaStatusChanged(self, status):
        # Play the song once we've loaded the media
        if status == QtMultimedia.QMediaPlayer.LoadedMedia:
            self.mediaPlayer.play()

        # When a song has finished playing, emit the end of media signal
        if status == QtMultimedia.QMediaPlayer.EndOfMedia:
            self.endOfMedia.emit()

        # If the file is invalid, just set the background to a solid color
        if status == QtMultimedia.QMediaPlayer.InvalidMedia:
            self.cdgImage.fill(0)


    @QtCore.pyqtSlot('qint64')
    def decodeCdgPackets(self, time):
        # CDG data should be processed at 300Hz (i.e. period of 3.3s)
        # Calculate how much time has elapsed since the last processing and
        # how many packets we should process
        numPacketsToProcess = (time - self.__previousReadTime)/(10.0/3)
        # Calculate and store the rounding error
        self.__fractionalPacketsToProcess += (numPacketsToProcess
                                              - int(numPacketsToProcess))
        
        # if __fractionalPacketsToProcess > 1, add those packets to
        # numPacketsToProcess
        numPacketsToProcess = (int(numPacketsToProcess)
                               + int (self.__fractionalPacketsToProcess))
        self.__fractionalPacketsToProcess -= \
            int(self.__fractionalPacketsToProcess)
        
        # Update __previousReadTime
        self.__previousReadTime = time

        # While we still have packets to process
        while ((self.currentBytePos + 24) < len(self.cdgBuffer)
               and numPacketsToProcess > 0):
            # The structure of each packet is:
            # typedef struct {
            #   char command;
            #   char instruction;
            #   char parityQ[2];
            #   char data[16];
            #   char parityP[4];
            # } SubCode
            # Each CD+G packet is 24 bytes long.
            subCode = (
                {'command': self.cdgBuffer[self.currentBytePos],
                 'instruction': self.cdgBuffer[self.currentBytePos + 1],
                  'parityQ': self.cdgBuffer[self.currentBytePos + 2:
                                            self.currentBytePos + 4],
                  'data': self.cdgBuffer[self.currentBytePos + 4:
                                         self.currentBytePos + 20],
                  'parityP': self.cdgBuffer[self.currentBytePos + 20:
                                            self.currentBytePos + 24]})
            # Only process CDG commands; ignore all other packets.
            if subCode['command'] & CDG_MASK == CDG_COMMAND:
                instruction = subCode['instruction'] & CDG_MASK
                if instruction in self.__processCdgInstructions:
                    self.__processCdgInstructions[instruction](subCode['data'])

            self.currentBytePos += 24
            numPacketsToProcess -= 1

        self.cdgImageUpdated.emit()


    ##### CDG command processing functions
    # This instruction clears the screen to "color." The command appears in
    # bunches and the repeat count is used to number them. You can ignore the
    # command if repeat != 0.
    # data interpreted as follows:
    # typdef struct {
    #   char color; // Only lower 4 bits are used
    #   char repeat; // Only lower 4 bits are used
    #   char filler[14];
    # } CDG_MemPreset
    def _exec_mem_preset(self, data):
        if len (data) >= 2:
            # Color
            color = data[0] & CDG_MASK
            repeat = data[1] & CDG_MASK
            # Only clear if repeat == 0; ignore otherwise
            if repeat == 0:
                self.cdgImage.fill (color)


    # The LOAD_COLOR_TBL_LO and LOAD_COLOR_TBL_HI commands load in the
    # colors for the color table. Their data field is interpreted as
    # typedef struct {
    #    short colorSpec[8];
    # } CDG_LoadCLUT
    # Each of the colorSpecs correspond to an entry in the color table.
    # In the LOAD_COLOR_TBL_LO instruction, they are indices 0-7. In the
    # LOAD_COLOR_TBL_HI instruction, they are indices 8-15. Each colorSpec
    # value is converted to RGB in the following way:
    #
    # [---high byte---]   [---low byte---]
    #  7 6 5 4 3 2 1 0     7 6 5 4 3 2 1 0
    #  X X r r r r g g     X X g g b b b b
    def _exec_load_color_tbl(self, data, colorTableIndex):
        # Check for 16 bytes
        if len(data) == 16:
            i = 0
            while i < 16:
                high_byte = data[i]
                low_byte = data[i + 1]

                red = (high_byte >> 2) & 0xF
                green = (((high_byte << 8) + (low_byte << 2)) >> 6) & 0xF
                blue = (low_byte) & 0xF

                # CD+G uses 4 bits for each RGB component, so we need to
                # convert this to 8 bits per component by multiplying by
                # 17 which is the same as (red << 4) + red.
                # e.g. if 4 bit red = 0xa, 8 bit red is 0xaa
                rgb_value = QtGui.qRgb(red * 17, green * 17, blue * 17)

                self.cdgImage.setColor(colorTableIndex, rgb_value)
                colorTableIndex += 1
                i += 2


    # This instruction loads the first 8 entries (0-7) of the color table.
    def _exec_load_color_tbl_lo(self, data):
        self._exec_load_color_tbl(data, 0)


    # This instruction loads the last 8 entries (8-16) of the color table.
    def _exec_load_color_tbl_hi(self, data):
        self._exec_load_color_tbl(data, 8)


    # The tile_block commands (norm and XOR) a load 12 x 6 tile of pixels to
    # row x column. The tile is stored using 1-bit graphics. The structure
    # contains two colors which are used when rendering the tile. The data is
    # interpreted as follows:
    # typedef struct {
    #   char color0;         // Only lower 4 bits are used, mask with 0x0F
    #   char color1;         // Only lower 4 bits are used, mask with 0x0F
    #   char row;            // Only lower 5 bits are used, mask with 0x1F
    #   char column;         // Only lower 6 bits are used, mask with 0x3F
    #   char tilePixels[12]; // Only lower 6 bits are used, mask with 0x3F
    # } CDG_Tile;
    # color0 and color1 describe the two colors (from the color table) which
    # are to be used when rendering the tile.
    # Colo0 is used for 0 bits and Color1 is used for 1 bits.
    #
    # Row and Column are the position of the tile. To convert to pixels,
    # multiply row by 12 and column by 6.
    #
    # tilePixels[] contains the actual bit values for the tile, six pixels
    # per byte. The uppermost valid bit of each byte (0x20) contains the
    # left-most pixel of each scanline of the tile.
    #
    # In the normal instruction, the corresponding colors from the color
    # table are simply copied to the screen.
    #
    # In the XOR variant, the color values are combined with the color values
    # already on  the screen using the XOR operator. Since CD+G only allows
    # a maximum of 16 colors, we are XORing the pixel values (0-15)
    # themselves, which correspond to the indices into the color lookup
    # table. We are not XORing the actual RGB values.
    def _exec_tile_block (self, data, is_xor):
        # Check for 16 bytes
        if len (data) == 16:
            # Parse data
            color0 = data[0] & 0x0F
            color1 = data[1] & 0x0F
            row = data[2] & 0x1F
            column = data[3] & 0x3F
            tilePixelData = [byte & 0x3F for byte in data[4:]]

            # Convert row to pixels
            y = row * 12
            for tilePixel in tilePixelData:
                # Convert column to pixels
                x = column * 6

                # We perform bit operations on only the last 6 bits of tilePixel
                for i in range (6):
                    # Only set pixels if we are within the CDG window
                    if y < CDG_HEIGHT and x < CDG_WIDTH:
                        # Check if last bit of tilePixel is a 0 or 1. This
                        # determines whether we use color0 or color1
                        if (tilePixel & 0x1):
                            # If this is the XOR variant, XOR the color found at
                            # the pixel with color1. Otherwise, for normal tile
                            # block operations, just set the pixel to color 1.
                            if is_xor:
                                self.cdgImageAsBitmap[y][x] = \
                                    (self.cdgImageAsBitmap[y][x] ^ color1)
                            else:
                                self.cdgImageAsBitmap[y][x] = color1
                        else:
                            # If this is the XOR variant, XOR the color found at
                            # the pixel with color1. Otherwise, for normal tile
                            # block operations, just set the pixel to color 1.
                            if is_xor:
                                self.cdgImageAsBitmap[y][x] = \
                                    (self.cdgImageAsBitmap[y][x] ^ color0)
                            else:
                                self.cdgImageAsBitmap[y][x] = color0
                        # Shift to the next bit
                    tilePixel = tilePixel >> 1
                    # Move to the next column
                    x -= 1
                # Move to the next row
                y += 1


    # This instruction loads a 12 x 6, 2 color tile and displays it normally
    def _exec_tile_block_norm(self, data):
        self._exec_tile_block(data, False)


    # This instruction loads a 12 x 6, 2 color tile and displays it using the
    # XOR method
    def _exec_load_tile_block_xor(self, data):
        self._exec_tile_block (data, True)


    # Since we can view the entire "safe area", we just set the entire
    # background to one color including the border with the memory preset
    # command.
    def _exec_border_preset(self, data):
        pass


    # Ignore these commands for now. These commands are rarely used.
    # TODO implement this
    def _exec_scroll_preset(self, data):
        pass


    # TODO implement this
    def _exec_scroll_copy(self, data):
        pass


    # TODO implement this
    def _exec_def_transparaent_color(self, data):
        pass