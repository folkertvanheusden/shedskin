### to compile this, copy lib/serial.* to the shedskin lib dir!

# Serial Bootstrap Loader software for the MSP430 embedded proccessor.
#
# (C) 2001-2003 Chris Liechti <cliechti@gmx.net>
# this is distributed under a free software license, see license.txt
#
# fixes from Colin Domoney
#
# modified to work with Shed Skin Python-to-C++ compiler by Mark Dufour
# Shed Skin homepage: http://mark.dufour.googlepages.com
#
# based on the application note slas96b.pdf from Texas Instruments, Inc.,
# Volker Rzehak
# additional infos from slaa089a.pdf

import serial
import sys, time, io, struct
import getopt

VERSION = "Revision: 1.39-telos-7 ".split()[1] #freeze the mspgcc CVS version, and tag telos

DEBUG = 0                                       #disable debug messages by default

#copy of the patch file provided by TI
#this part is (C) by Texas Instruments
PATCH = b"""@0220
31 40 1A 02 09 43 B0 12 2A 0E B0 12 BA 0D 55 42
0B 02 75 90 12 00 1F 24 B0 12 BA 02 55 42 0B 02
75 90 16 00 16 24 75 90 14 00 11 24 B0 12 84 0E
06 3C B0 12 94 0E 03 3C 21 53 B0 12 8C 0E B2 40
10 A5 2C 01 B2 40 00 A5 28 01 30 40 42 0C 30 40
76 0D 30 40 AC 0C 16 42 0E 02 17 42 10 02 E2 B2
08 02 14 24 B0 12 10 0F 36 90 00 10 06 28 B2 40
00 A5 2C 01 B2 40 40 A5 28 01 D6 42 06 02 00 00
16 53 17 83 EF 23 B0 12 BA 02 D3 3F B0 12 10 0F
17 83 FC 23 B0 12 BA 02 D0 3F 18 42 12 02 B0 12
10 0F D2 42 06 02 12 02 B0 12 10 0F D2 42 06 02
13 02 38 E3 18 92 12 02 BF 23 E2 B3 08 02 BC 23
30 41
q
"""

#These BSL's are (C) by TI. They come with the application note slaa089a
F1X_BSL = b"""@0220
24 02 2E 02 31 40 20 02 2B D2 C0 43 EA FF 32 C2
F2 C0 32 00 00 00 B2 40 80 5A 20 01 F2 40 85 00
57 00 F2 40 80 00 56 00 E2 D3 21 00 E2 D3 22 00
E2 C3 26 00 E2 C2 2A 00 E2 C2 2E 00 B2 40 10 A5
2C 01 B2 40 00 A5 28 01 3B C0 3A 00 B0 12 D6 04
82 43 12 02 09 43 36 40 0A 02 37 42 B0 12 AC 05
C6 4C 00 00 16 53 17 83 F9 23 D2 92 0C 02 0D 02
28 20 55 42 0B 02 75 90 12 00 80 24 75 90 10 00
6D 24 B0 12 9C 04 55 42 0B 02 75 90 18 00 31 24
75 90 1E 00 B8 24 75 90 20 00 17 24 2B B2 11 24
75 90 16 00 22 24 75 90 14 00 B3 24 75 90 1A 00
18 24 75 90 1C 00 45 24 04 3C B0 12 36 05 BE 3F
21 53 B0 12 3C 05 BA 3F 03 43 B0 12 36 05 D2 42
0E 02 56 00 D2 42 0F 02 57 00 D2 42 10 02 16 02
AD 3F B0 12 36 05 10 42 0E 02 16 42 0E 02 15 43
07 3C 36 40 FE FF B2 40 06 A5 10 02 35 40 0C 00
B2 40 00 A5 2C 01 92 42 10 02 28 01 B6 43 00 00
92 B3 2C 01 FD 23 15 83 F3 23 36 90 FE FF CD 27
37 40 80 00 36 F0 80 FF 36 90 00 11 0E 28 07 57
36 F0 00 FF 36 90 00 12 08 28 07 57 36 F0 00 FE
04 3C 16 42 0E 02 17 42 10 02 35 43 75 96 03 20
17 83 FC 23 B2 3F 82 46 00 02 B3 3F 36 40 E0 FF
37 40 20 00 B0 12 AC 05 7C 96 01 24 2B D3 17 83
F9 23 2B C2 B0 12 9C 04 2B D2 9F 3F 16 42 0E 02
17 42 10 02 2B B2 38 24 3B D0 10 00 B0 12 AC 05
36 90 00 10 06 2C 36 90 00 01 09 2C C6 4C 00 00
25 3C B2 40 00 A5 2C 01 B2 40 40 A5 28 01 16 B3
03 20 C2 4C 14 02 1A 3C C2 4C 15 02 86 9A FD FF
08 24 2B D3 3B B0 20 00 04 20 3B D0 20 00 82 46
00 02 36 90 01 02 04 28 3B D2 3B B0 10 00 02 24
3B C0 32 00 1A 42 14 02 86 4A FF FF 16 53 17 83
CD 23 B0 12 9C 04 61 3F B0 12 AC 05 17 83 FC 23
B0 12 9C 04 5E 3F B2 40 F0 0F 0E 02 B2 40 10 00
10 02 B2 40 80 00 0A 02 D2 42 10 02 0C 02 D2 42
10 02 0D 02 82 43 12 02 09 43 36 40 0A 02 27 42
7C 46 B0 12 40 05 17 83 FB 23 16 42 0E 02 17 42
10 02 36 90 00 01 0A 28 B2 46 14 02 5C 42 14 02
B0 12 40 05 17 83 5C 42 15 02 01 3C 7C 46 B0 12
40 05 17 83 EE 23 B2 E3 12 02 5C 42 12 02 B0 12
40 05 5C 42 13 02 B0 12 40 05 E0 3E 18 42 12 02
B0 12 AC 05 C2 4C 12 02 B0 12 AC 05 C2 4C 13 02
38 E3 3B B2 0A 24 86 9A FE FF 07 24 3B B0 20 00
04 20 16 53 82 46 00 02 2B D3 18 92 12 02 08 23
2B B3 06 23 30 41 E2 B2 28 00 FD 27 E2 B2 28 00
FD 23 B2 40 24 02 60 01 E2 B2 28 00 FD 27 15 42
70 01 05 11 05 11 05 11 82 45 02 02 05 11 82 45
04 02 B2 80 1E 00 04 02 57 42 16 02 37 80 03 00
05 11 05 11 17 53 FD 23 35 50 40 A5 82 45 2A 01
35 42 B2 40 24 02 60 01 92 92 70 01 02 02 FC 2F
15 83 F7 23 09 43 7C 40 90 00 02 3C 7C 40 A0 00
C2 43 07 02 C9 EC 12 02 19 E3 1B C3 55 42 07 02
55 45 56 05 00 55 0C 2E 2E 2E 2E 2E 2E 2E 2E 1A
34 34 92 42 70 01 72 01 B2 50 0C 00 72 01 07 3C
1B B3 0B 20 82 43 62 01 92 B3 62 01 FD 27 E2 C3
21 00 0A 3C 4C 11 F6 2B 1B E3 82 43 62 01 92 B3
62 01 FD 27 E2 D3 21 00 92 52 02 02 72 01 D2 53
07 02 F0 90 0C 00 61 FC D1 23 30 41 C2 43 09 02
1B C3 55 42 09 02 55 45 BC 05 00 55 0C 56 56 56
56 56 56 56 56 36 76 00 E2 B2 28 00 FD 23 92 42
70 01 72 01 92 52 04 02 72 01 82 43 62 01 92 B3
62 01 FD 27 E2 B2 28 00 1E 28 2B D3 1C 3C 4C 10
1A 3C 82 43 62 01 92 B3 62 01 FD 27 E2 B2 28 00
01 28 1B E3 1B B3 01 24 2B D3 C9 EC 12 02 19 E3
0A 3C 82 43 62 01 92 B3 62 01 FD 27 E2 B2 28 00
E6 2B 4C 10 1B E3 92 52 02 02 72 01 D2 53 09 02
C0 3F 82 43 62 01 92 B3 62 01 FD 27 E2 B2 28 00
01 2C 2B D3 30 41
q
"""

F4X_BSL = b"""@0220
24 02 2E 02 31 40 20 02 2B D2 C0 43 EA FF 32 C2
F2 C0 32 00 00 00 B2 40 80 5A 20 01 32 D0 40 00
C2 43 50 00 F2 40 98 00 51 00 F2 C0 80 00 52 00
D2 D3 21 00 D2 D3 22 00 D2 C3 26 00 E2 C3 22 00
E2 C3 26 00 B2 40 10 A5 2C 01 B2 40 00 A5 28 01
3B C0 3A 00 B0 12 DE 04 82 43 12 02 09 43 36 40
0A 02 37 42 B0 12 B4 05 C6 4C 00 00 16 53 17 83
F9 23 D2 92 0C 02 0D 02 28 20 55 42 0B 02 75 90
12 00 80 24 75 90 10 00 6D 24 B0 12 A4 04 55 42
0B 02 75 90 18 00 31 24 75 90 1E 00 B8 24 75 90
20 00 17 24 2B B2 11 24 75 90 16 00 22 24 75 90
14 00 B3 24 75 90 1A 00 18 24 75 90 1C 00 45 24
04 3C B0 12 3E 05 BE 3F 21 53 B0 12 44 05 BA 3F
03 43 B0 12 3E 05 D2 42 0E 02 50 00 D2 42 0F 02
51 00 D2 42 10 02 16 02 AD 3F B0 12 3E 05 10 42
0E 02 16 42 0E 02 15 43 07 3C 36 40 FE FF B2 40
06 A5 10 02 35 40 0C 00 B2 40 00 A5 2C 01 92 42
10 02 28 01 B6 43 00 00 92 B3 2C 01 FD 23 15 83
F3 23 36 90 FE FF CD 27 37 40 80 00 36 F0 80 FF
36 90 00 11 0E 28 07 57 36 F0 00 FF 36 90 00 12
08 28 07 57 36 F0 00 FE 04 3C 16 42 0E 02 17 42
10 02 35 43 75 96 03 20 17 83 FC 23 B2 3F 82 46
00 02 B3 3F 36 40 E0 FF 37 40 20 00 B0 12 B4 05
7C 96 01 24 2B D3 17 83 F9 23 2B C2 B0 12 A4 04
2B D2 9F 3F 16 42 0E 02 17 42 10 02 2B B2 38 24
3B D0 10 00 B0 12 B4 05 36 90 00 10 06 2C 36 90
00 01 09 2C C6 4C 00 00 25 3C B2 40 00 A5 2C 01
B2 40 40 A5 28 01 16 B3 03 20 C2 4C 14 02 1A 3C
C2 4C 15 02 86 9A FD FF 08 24 2B D3 3B B0 20 00
04 20 3B D0 20 00 82 46 00 02 36 90 01 02 04 28
3B D2 3B B0 10 00 02 24 3B C0 32 00 1A 42 14 02
86 4A FF FF 16 53 17 83 CD 23 B0 12 A4 04 61 3F
B0 12 B4 05 17 83 FC 23 B0 12 A4 04 5E 3F B2 40
F0 0F 0E 02 B2 40 10 00 10 02 B2 40 80 00 0A 02
D2 42 10 02 0C 02 D2 42 10 02 0D 02 82 43 12 02
09 43 36 40 0A 02 27 42 7C 46 B0 12 48 05 17 83
FB 23 16 42 0E 02 17 42 10 02 36 90 00 01 0A 28
B2 46 14 02 5C 42 14 02 B0 12 48 05 17 83 5C 42
15 02 01 3C 7C 46 B0 12 48 05 17 83 EE 23 B2 E3
12 02 5C 42 12 02 B0 12 48 05 5C 42 13 02 B0 12
48 05 E0 3E 18 42 12 02 B0 12 B4 05 C2 4C 12 02
B0 12 B4 05 C2 4C 13 02 38 E3 3B B2 0A 24 86 9A
FE FF 07 24 3B B0 20 00 04 20 16 53 82 46 00 02
2B D3 18 92 12 02 08 23 2B B3 06 23 30 41 E2 B3
20 00 FD 27 E2 B3 20 00 FD 23 B2 40 24 02 60 01
E2 B3 20 00 FD 27 15 42 70 01 05 11 05 11 05 11
82 45 02 02 05 11 82 45 04 02 B2 80 1E 00 04 02
57 42 16 02 37 80 03 00 05 11 05 11 17 53 FD 23
35 50 40 A5 82 45 2A 01 35 42 B2 40 24 02 60 01
92 92 70 01 02 02 FC 2F 15 83 F7 23 09 43 7C 40
90 00 02 3C 7C 40 A0 00 C2 43 07 02 C9 EC 12 02
19 E3 1B C3 55 42 07 02 55 45 5E 05 00 55 0C 2E
2E 2E 2E 2E 2E 2E 2E 1A 34 34 92 42 70 01 72 01
B2 50 0C 00 72 01 07 3C 1B B3 0B 20 82 43 62 01
92 B3 62 01 FD 27 D2 C3 21 00 0A 3C 4C 11 F6 2B
1B E3 82 43 62 01 92 B3 62 01 FD 27 D2 D3 21 00
92 52 02 02 72 01 D2 53 07 02 F0 90 0C 00 59 FC
D1 23 30 41 C2 43 09 02 1B C3 55 42 09 02 55 45
C4 05 00 55 0C 56 56 56 56 56 56 56 56 36 76 00
E2 B3 20 00 FD 23 92 42 70 01 72 01 92 52 04 02
72 01 82 43 62 01 92 B3 62 01 FD 27 E2 B3 20 00
1E 28 2B D3 1C 3C 4C 10 1A 3C 82 43 62 01 92 B3
62 01 FD 27 E2 B3 20 00 01 28 1B E3 1B B3 01 24
2B D3 C9 EC 12 02 19 E3 0A 3C 82 43 62 01 92 B3
62 01 FD 27 E2 B3 20 00 E6 2B 4C 10 1B E3 92 52
02 02 72 01 D2 53 09 02 C0 3F 82 43 62 01 92 B3
62 01 FD 27 E2 B3 20 00 01 2C 2B D3 30 41
q
"""

#cpu types for "change baudrate"
#use strings as ID so that they can be used in outputs too
F1x                     = "F1x family"
F4x                     = "F4x family"

#known device list
deviceids = {
   0xf149: F1x,
   0xf16c: F1x, #for telosb
   0xf112: F1x,
   0xf413: F4x,
   0xf123: F1x,
   0xf449: F4x,
   0x1232: F1x,
}

class BSLException(Exception):
   pass

# shed skin: the following used to be LowLevel class attributes 
#Constants
MODE_SSP                = 0
MODE_BSL                = 1

BSL_SYNC                = 0x80
BSL_TXPWORD             = 0x10
BSL_TXBLK               = 0x12 #Transmit block to boot loader
BSL_RXBLK               = 0x14 #Receive  block from boot loader
BSL_ERASE               = 0x16 #Erase one segment
BSL_MERAS               = 0x18 #Erase complete FLASH memory
BSL_CHANGEBAUD          = 0x20 #Change baudrate
BSL_LOADPC              = 0x1A #Load PC and start execution
BSL_TXVERSION           = 0x1E #Get BSL version

#Upper limit of address range that might be modified by
#"BSL checksum bug".
BSL_CRITICAL_ADDR       = 0x0A00

#Header Definitions
CMD_FAILED              = 0x70
DATA_FRAME              = 0x80
DATA_ACK                = 0x90
DATA_NAK                = 0xA0

QUERY_POLL              = 0xB0
QUERY_RESPONSE          = 0x50

OPEN_CONNECTION         = 0xC0
ACK_CONNECTION          = 0x40

DEFAULT_TIMEOUT         =   1
DEFAULT_PROLONG         =  10
MAX_FRAME_SIZE          = 256
MAX_DATA_BYTES          = 250
MAX_DATA_WORDS          = 125

MAX_FRAME_COUNT         = 16

#Error messages
ERR_COM                 = "Unspecific error"
ERR_RX_NAK              = "NAK received (wrong password?)"
#ERR_CMD_NOT_COMPLETED   = "Command did not send ACK: indicates that it didn't complete correctly"
ERR_CMD_FAILED          = "Command failed, is not defined or is not allowed"
ERR_BSL_SYNC            = "Bootstrap loader synchronization error"
ERR_FRAME_NUMBER        = "Frame sequence number error."

class LowLevel:
   "lowlevel communication"

   def calcChecksum(self, data, length):
       """Calculates a checksum of "data"."""
       checksum = 0

       for i in range(length/2):
           checksum = checksum ^ (data[i*2] | (data[i*2+1] << 8))    #xor-ing
       return 0xffff & (checksum ^ 0xffff)         #inverting

   def __init__(self, aTimeout=-1, aProlongFactor=-1): # shed skin : change default None arguments
       """init bsl object, don't connect yet"""
       if aTimeout == -1: #is None:
           self.timeout = DEFAULT_TIMEOUT
       else:
           self.timeout = aTimeout
       if aProlongFactor == -1: #is None:
           self.prolongFactor = DEFAULT_PROLONG
       else:
           self.prolongFactor = aProlongFactor

       #flags for inverted use of control pins
       #used for some hardware
       self.invertRST = 0
       self.invertTEST = 0
       self.swapRSTTEST = 0
       self.telosLatch = 0
       self.telosI2C = 0

       self.protocolMode = MODE_BSL
       self.BSLMemAccessWarning = 0                #Default: no warning.
       self.slowmode = 0

   def comInit(self, port):
       """Tries to open the serial port given and
       initialises the port and variables.
       The timeout and the number of allowed errors is multiplied by
       'aProlongFactor' after transmission of a command to give
       plenty of time to the micro controller to finish the command.
       Returns zero if the function is successful."""
       if DEBUG > 1: sys.stderr.write("* comInit()\n")
       self.seqNo = 0
       self.reqNo = 0
       self.rxPtr = 0
       self.txPtr = 0
       # Startup-Baudrate: 9600,8,E,1, 1s timeout

       # shed skin : argument change
       self.serialport = serial.Serial(port, 9600, 8, 'E', 1, self.timeout, 0, 0)
       #self.serialport = serial.Serial(
       #    port,
       #    9600,
       #    parity = serial.PARITY_EVEN,
       #    timeout = self.timeout
       #)

       # shed skin
       #if DEBUG: sys.stderr.write("using serial port %r\n" % self.serialport.portstr)
       self.SetRSTpin()                        #enable power
       self.SetTESTpin()                       #enable power
       self.serialport.flushInput()
       self.serialport.flushOutput()

   def comDone(self):
       """Closes the used serial port.
       This function must be called at the end of a program,
       otherwise the serial port might not be released and can not be
       used in other programs.
       Returns zero if the function is successful."""
       if DEBUG > 1: sys.stderr.write("* comDone()")
       self.SetRSTpin(1)                       #disable power
       self.SetTESTpin(0)                      #disable power
       self.serialport.close()

   def comRxHeader(self):
       """receive header and split data"""
       if DEBUG > 1: sys.stderr.write("* comRxHeader()\n")

       hdr = self.serialport.read(1)
       if not hdr: raise BSLException("Timeout")
       rxHeader = hdr[0] & 0xf0;
       rxNum    = hdr[0] & 0x0f;

       if self.protocolMode == MODE_BSL:
           self.reqNo = 0
           self.seqNo = 0
           rxNum = 0
       if DEBUG > 1: sys.stderr.write("* comRxHeader() OK\n")
       return rxHeader, rxNum

   def comRxFrame(self, rxNum):
       if DEBUG > 1: sys.stderr.write("* comRxFrame()\n")
       rxFrame = b'%c' % (DATA_FRAME | rxNum)

       if DEBUG > 2: sys.stderr.write("  comRxFrame() header...\n")
       rxFramedata = self.serialport.read(3)
       if len(rxFramedata) != 3: raise BSLException("Timeout")
       rxFrame = rxFrame + rxFramedata

       if DEBUG > 3: sys.stderr.write("  comRxFrame() check header...\n")
       if rxFrame[1] == 0 and rxFrame[2] == rxFrame[3]:   #Add. header info. correct?
           rxLengthCRC = rxFrame[2] + 2       #Add CRC-Bytes to length
           if DEBUG > 2: sys.stderr.write("  comRxFrame() receiving data, size: %s\n" % rxLengthCRC)

           rxFramedata = self.serialport.read(rxLengthCRC)
           if len(rxFramedata) != rxLengthCRC: raise BSLException("Timeout")
           rxFrame = rxFrame + rxFramedata
           #Check received frame:
           if DEBUG > 3: sys.stderr.write("  comRxFrame() crc check\n")
           #rxLength+4: Length with header but w/o CRC:
           checksum = self.calcChecksum(rxFrame, rxFrame[2] + 4)
           if rxFrame[rxFrame[2]+4] == (0xff & checksum) and \
              rxFrame[rxFrame[2]+5] == (0xff & (checksum >> 8)): #Checksum correct?
               #Frame received correctly (=> send next frame)
               if DEBUG > 2: sys.stderr.write("* comRxFrame() OK\n")
               return rxFrame
           else:
               if DEBUG: sys.stderr.write("  comRxFrame() Checksum wrong\n")
       else:
           if DEBUG: sys.stderr.write("  comRxFrame() Header corrupt %r" % rxFrame)
       raise BSLException(ERR_COM)            #Frame has errors!

   def comTxHeader(self, txHeader):
       """send header"""
       if DEBUG > 1: sys.stderr.write("* txHeader()\n")
       self.serialport.write(txHeader)

   def comTxRx(self, cmd, dataOutstr, length): # shed skin: change name of dataOut
       """Sends the command cmd with the data given in dataOut to the
       microcontroller and expects either an acknowledge or a frame
       with result from the microcontroller.  The results are stored
       in dataIn (if not a NULL pointer is passed).
       In this routine all the necessary protocol stuff is handled.
       Returns zero if the function was successful."""
       if DEBUG > 1: sys.stderr.write("* comTxRx()\n")
       #txFrame     = [] # shed skin 
       rxHeader    = 0
       rxNum       = 0

       dataOut = list(dataOutstr)     #convert to a list for simpler data fill in
       #Transmitting part ----------------------------------------
       #Prepare data for transmit
       # shed skin : put chr around (0xff) and (0), or it cannot work (because of string.join below)
       if (length % 2) != 0:
           #/* Fill with one byte to have even number of bytes to send */
           if self.protocolMode == MODE_BSL:
               dataOut.append(0xFF)  #fill with 0xFF
           else:
               dataOut.append(0)     #fill with zero

       txFrame = b"%c%c%c%c" % (DATA_FRAME | self.seqNo, cmd, len(dataOut), len(dataOut))

       self.reqNo = (self.seqNo + 1) % MAX_FRAME_COUNT

       txFrame = txFrame + bytes(dataOut)
       checksum = self.calcChecksum(txFrame, length + 4)
       txFrame = txFrame + b'%c' % (checksum & 0xff)
       txFrame = txFrame + b'%c' % ((checksum >> 8) & 0xff)

       accessAddr = (0x0212 + (checksum^0xffff)) & 0xfffe  #0x0212: Address of wCHKSUM
       if self.BSLMemAccessWarning and accessAddr < BSL_CRITICAL_ADDR:
           sys.stderr.write("WARNING: This command might change data at address %04x or %04x!\n" % (accessAddr, accessAddr + 1))

       self.serialport.flushInput()                #clear receiving queue
       #TODO: Check after each transmitted character,
       #TODO: if microcontroller did send a character (probably a NAK!).
       for c in txFrame:
           self.serialport.write(b'%c' % c)
           if DEBUG > 3: sys.stderr.write("\ttx %02x" % c)
           #if self.serialport.inWaiting(): break  #abort when BSL replies, probably NAK
       else:
           if DEBUG > 1: sys.stderr.write( "  comTxRx() transmit OK\n")

       #Receiving part -------------------------------------------
       rxHeader, rxNum = self.comRxHeader()        #receive header
       if DEBUG > 1: sys.stderr.write("  comTxRx() rxHeader=0x%02x, rxNum=%d, seqNo=%d, reqNo=%s\n" % (rxHeader, rxNum, self.seqNo, self.reqNo))
       if rxHeader == DATA_ACK:               #acknowledge/OK
           if DEBUG > 2: sys.stderr.write("  comTxRx() DATA_ACK\n")
           if rxNum == self.reqNo:
               self.seqNo = self.reqNo
               if DEBUG > 2: sys.stderr.write("* comTxRx() DATA_ACK OK\n")
               return          #Acknowledge received correctly => next frame
           raise BSLException(ERR_FRAME_NUMBER)
       elif rxHeader == DATA_NAK:             #not acknowledge/error
           if DEBUG > 2: sys.stderr.write("* comTxRx() DATA_NAK\n")
           raise BSLException(ERR_RX_NAK)
       elif rxHeader == DATA_FRAME:           #receive data
           if DEBUG > 2: sys.stderr.write("* comTxRx() DATA_FRAME\n")
           if rxNum == self.reqNo:
               rxFrame = self.comRxFrame(rxNum)
               return rxFrame
           raise BSLException(ERR_FRAME_NUMBER)
       elif rxHeader == CMD_FAILED:           #Frame ok, but command failed.
           if DEBUG > 2: sys.stderr.write("*  comTxRx() CMD_FAILED\n")
           raise BSLException(ERR_CMD_FAILED)

       raise BSLException("Unknown header 0x%02x\nAre you downloading to RAM into an old device that requires the patch? Try option -U" % rxHeader)

   def SetDTR(self, level, invert):
       """Controls DTR pin (0: GND; 1: VCC; unless inverted flag is set)"""
       if invert:
           self.serialport.setDTR(not level)
       else:
           self.serialport.setDTR(level)
       if self.slowmode:
           time.sleep(0.010)

   def SetRTS(self, level, invert):
       """Controls RTS pin (0: GND; 1: VCC; unless inverted flag is set)"""
       if invert:
           self.serialport.setRTS(not level)
       else:
           self.serialport.setRTS(level)
       if self.slowmode:
           time.sleep(0.010)

   def SetRSTpin(self, level=1):
       """Controls RST/NMI pin (0: GND; 1: VCC; unless inverted flag is set)"""
       if self.swapRSTTEST:
           self.SetRTS(level, self.invertRST)
       else:
           self.SetDTR(level, self.invertRST)

   def SetTESTpin(self, level=1):
       """Controls TEST pin (inverted on board: 0: VCC; 1: GND; unless inverted flag is set)"""
       if self.swapRSTTEST:
           self.SetDTR(level, self.invertTEST)
       else:
           self.SetRTS(level, self.invertTEST)

   def telosSetSCL(self, level):
       self.serialport.setRTS(not level)

   def telosSetSDA(self, level):
       self.serialport.setDTR(not level)

   def telosI2CStart(self):
       self.telosSetSDA(1)
       self.telosSetSCL(1)
       self.telosSetSDA(0)

   def telosI2CStop(self):
       self.telosSetSDA(0)
       self.telosSetSCL(1)
       self.telosSetSDA(1)

   def telosI2CWriteBit(self, bit):
       self.telosSetSCL(0)
       self.telosSetSDA(bit)
       time.sleep(2e-6)
       self.telosSetSCL(1)
       time.sleep(1e-6)
       self.telosSetSCL(0)

   def telosI2CWriteByte(self, byte):
       self.telosI2CWriteBit( byte & 0x80 );
       self.telosI2CWriteBit( byte & 0x40 );
       self.telosI2CWriteBit( byte & 0x20 );
       self.telosI2CWriteBit( byte & 0x10 );
       self.telosI2CWriteBit( byte & 0x08 );
       self.telosI2CWriteBit( byte & 0x04 );
       self.telosI2CWriteBit( byte & 0x02 );
       self.telosI2CWriteBit( byte & 0x01 );
       self.telosI2CWriteBit( 0 );  # "acknowledge"

   def telosI2CWriteCmd(self, addr, cmdbyte):
       self.telosI2CStart()
       self.telosI2CWriteByte( 0x90 | (addr << 1) )
       self.telosI2CWriteByte( cmdbyte )
       self.telosI2CStop()

   def telosBReset(self,invokeBSL=0):

       # "BSL entry sequence at dedicated JTAG pins"
       # rst !s0: 0 0 0 0 1 1
       # tck !s1: 1 0 1 0 0 1
       #   s0|s1: 1 3 1 3 2 0

       # "BSL entry sequence at shared JTAG pins"
       # rst !s0: 0 0 0 0 1 1
       # tck !s1: 0 1 0 1 1 0
       #   s0|s1: 3 1 3 1 0 2

       if invokeBSL:
         self.telosI2CWriteCmd(0,1)
         self.telosI2CWriteCmd(0,3)
         self.telosI2CWriteCmd(0,1)
         self.telosI2CWriteCmd(0,3)
         self.telosI2CWriteCmd(0,2)
         self.telosI2CWriteCmd(0,0)
       else:
         self.telosI2CWriteCmd(0,3)
         self.telosI2CWriteCmd(0,2)
       self.telosI2CWriteCmd(0,0)
       time.sleep(0.250)       #give MSP430's oscillator time to stabilize
       self.serialport.flushInput()  #clear buffers

   def bslReset(self, invokeBSL=0):
       """Applies BSL entry sequence on RST/NMI and TEST/VPP pins
       Parameters:
           invokeBSL = 1: complete sequence
           invokeBSL = 0: only RST/NMI pin accessed

       RST is inverted twice on boot loader hardware
       TEST is inverted (only once)
       Need positive voltage on DTR, RTS for power-supply of hardware"""
       if self.telosI2C:
         self.telosBReset(invokeBSL)
         return

       if DEBUG > 1: sys.stderr.write("* bslReset(invokeBSL=%s)\n" % invokeBSL)
       self.SetRSTpin(1)       #power suply
       self.SetTESTpin(1)      #power suply
       time.sleep(0.250)       #charge capacitor on boot loader hardware

       if self.telosLatch:
         self.SetTESTpin(0)
         self.SetRSTpin(0)
         self.SetTESTpin(1)

       self.SetRSTpin(0)       #RST  pin: GND
       if invokeBSL:
           self.SetTESTpin(1)  #TEST pin: GND
           self.SetTESTpin(0)  #TEST pin: Vcc
           self.SetTESTpin(1)  #TEST pin: GND
           self.SetTESTpin(0)  #TEST pin: Vcc
           self.SetRSTpin (1)  #RST  pin: Vcc
           self.SetTESTpin(1)  #TEST pin: GND
       else:
           self.SetRSTpin(1)   #RST  pin: Vcc
       time.sleep(0.250)       #give MSP430's oscillator time to stabilize

       self.serialport.flushInput()    #clear buffers

   def bslSync(self,wait=0):
       """Transmits Synchronization character and expects to receive Acknowledge character
       if wait is 0 it must work the first time. otherwise if wait is 1
       it is retried (forever).
       """
       loopcnt = 5                                 #Max. tries to get synchronization

       if DEBUG > 1: sys.stderr.write("* bslSync(wait=%d)\n" % wait)
       while wait or loopcnt:
           loopcnt = loopcnt - 1                   #count down tries
           self.serialport.flushInput()            #clear input, in case a prog is running

           self.serialport.write(b'%c' % BSL_SYNC)   #Send synchronization byte
           c = self.serialport.read(1)             #read answer
           if c == (b'%c' % DATA_ACK):             #ACk
               if DEBUG > 1: sys.stderr.write("  bslSync() OK\n")
               return                              #Sync. successful
           elif not c:                             #timeout
                   if loopcnt > 4:
                       if DEBUG > 1:
                           sys.stderr.write("  bslSync() timeout, retry ...\n")
                   elif loopcnt == 4:
                       #nmi may have caused the first reset to be ignored, try again
                       self.bslReset(0)
                       self.bslReset(1)
                   elif loopcnt > 0:
                       if DEBUG > 1:
                           sys.stderr.write("  bslSync() timeout, retry ...\n")
                   else :
                       if DEBUG > 1:
                           sys.stderr.write("  bslSync() timeout\n")
           else:                                   #garbage
               if DEBUG > 1: sys.stderr.write("  bslSync() failed (0x%02x), retry ...\n" % c)

               raise BSLException(ERR_BSL_SYNC)       #Sync. failed

   def bslTxRx(self, cmd, addr, length = 0, blkout = None, wait=0):
       """Transmits a command (cmd) with its parameters:
       start-address (addr), length (len) and additional
       data (blkout) to boot loader.
       wait specified if the bsl sync should be tried once or
       repeated, forever
       Parameters return by boot loader are passed via blkin.
       """
       if DEBUG > 1: sys.stderr.write("* bslTxRx()\n")

       if cmd == BSL_TXBLK:
           #Align to even start address
           if (addr % 2) != 0:
               addr = addr - 1                     #Decrement address and
               # shed skin : bug detected
               #blkout = chr(0xFF) + blkOut         #fill first byte of blkout with 0xFF
               blkout = b'\xff' + blkout         #fill first byte of blkout with 0xFF
               length = length + 1
           #Make sure that len is even
           if (length % 2) != 0:
               blkout = blkout + b'\xff'         #Inc. len and fill last byte of blkout with 0xFF
               length = length + 1

       elif cmd == BSL_RXBLK:
           #Align to even start address
           if (addr % 2) != 0:
               addr = addr - 1                     #Decrement address but
               length = length + 1                 #request an additional byte
           #Make sure that len is even
           if (length % 2) != 0:
               length = length + 1

       #if cmd == BSL_TXBLK or cmd == BSL_TXPWORD:
       #    length = len + 4

       #Add necessary information data to frame
       # shed skin : use shed skin struct module
       dataOut = struct.pack("<HH", addr, length)

       if blkout: #Copy data out of blkout into frame
           dataOut = dataOut + blkout

       self.bslSync(wait)                          #synchronize BSL
       rxFrame = self.comTxRx(cmd, dataOut, len(dataOut))  #Send frame
       if rxFrame:                                 #test answer
           return rxFrame[4:] #return only data w/o [hdr,null,len,len]
       else:
           return rxFrame

class Segment:
   """store a string with memory contents along with its startaddress"""
   def __init__(self, startaddress = 0, data=None):
       if data is None:
           self.data = b''
       else:
           self.data = data
       self.startaddress = startaddress

   def __getitem__(self, index):
       return self.data[index]

   def __len__(self):
       return len(self.data)

   def __repr__(self):
       return "Segment(startaddress = 0x%04x, data=%r)" % (self.startaddress, self.data)

class Memory:
   """represent memory contents. with functions to load files"""
   def __init__(self, filename=None):
       self.segments = []
       if filename:
           self.filename = filename
           self.loadFile(filename)

   def append(self, seg):
       self.segments.append(seg)

   def __getitem__(self, index):
       return self.segments[index]

   def __len__(self):
       return len(self.segments)

   def loadIHex(self, file):
       """load data from a (opened) file in Intel-HEX format"""
       segmentdata = []
       currentAddr = 0
       startAddr   = 0
       lines = file.readlines()
       for l in lines:
           if l[0] != ord(':'): raise BSLException("File Format Error\n")
           l = l.strip()       #fix CR-LF issues...
           length  = int(l[1:3],16)
           address = int(l[3:7],16)
           type    = int(l[7:9],16)
           check   = int(l[-2:],16)
           if type == 0x00:
               if currentAddr != address:
                   if segmentdata:
                       self.segments.append( Segment(startAddr, bytes(segmentdata) ) )
                   startAddr = currentAddr = address
                   segmentdata = []
               for i in range(length):
                   segmentdata.append( int(l[9+2*i:11+2*i],16) )
               currentAddr = length + currentAddr
           elif type in (0x01, 0x02, 0x03, 0x04, 0x05):
               pass
           else:
               sys.stderr.write("Ignored unknown field (type 0x%02x) in ihex file.\n" % type)
       if segmentdata:
           self.segments.append( Segment(startAddr, bytes(segmentdata) ) )

   def loadTIText(self, file):
       """load data from a (opened) file in TI-Text format"""
       next        = 1
       startAddr   = 0
       segmentdata = []
       #Convert data for MSP430, TXT-File is parsed line by line
       while next >= 1:
           #Read one line
           l = file.readline()
           if not l: break #EOF
           l = l.strip()
           if l[0] == ord('q'): break
           elif l[0] == ord('@'):        #if @ => new address => send frame and set new addr.
               #create a new segment
               if segmentdata:
                   self.segments.append( Segment(startAddr, bytes(segmentdata)) )
               startAddr = int(l[1:],16)
               segmentdata = []
           else:
               for i in l.split():
                   segmentdata.append(int(i,16))
       if segmentdata:
           self.segments.append( Segment(startAddr, bytes(segmentdata)) )

   def loadELF(self, file):
       """load data from a (opened) file in ELF object format.
       File must be seekable"""
# shed skin
       raise NotImplementedError("support for ELF files has been disabled")
#       import elf
#       obj = elf.ELFObject()
#       obj.fromFile(file)
#       if obj.e_type != elf.ELFObject.ET_EXEC:
#           raise Exception("No executable")
#       for section in obj.getSections():
#           if DEBUG:
#               sys.stderr.write("ELF section %s at 0x%04x %d bytes\n" % (section.name, section.lma, len(section.data)))
#           if len(section.data):
#               self.segments.append( Segment(section.lma, section.data) )

   def loadFile(self, filename):
       """fill memory with the contents of a file. file type is determined from extension"""
       #TODO: do a contents based detection
       if filename[-4:].lower() == '.txt':
           self.loadTIText(open(filename, "rb"))
       elif filename[-4:].lower() in ('.a43', '.hex'):
           self.loadIHex(open(filename, "rb"))
       else:
           self.loadELF(open(filename, "rb"))

   def getMemrange(self, fromadr, toadr):
       """get a range of bytes from the memory. unavailable values are filled with 0xff."""
       res = b''
       toadr = toadr + 1   #python indxes are excluding end, so include it
       while fromadr < toadr:
           #print "fromto: %04x %04x" % (fromadr, toadr)
           for seg in self.segments:
               #print seg
               segend = seg.startaddress + len(seg.data)
               if seg.startaddress <= fromadr and fromadr < segend:
                   #print "startok 0x%04x %d" % (seg.startaddress, len(seg.data))
                   #print ("0x%04x "*3) % (segend, fromadr, toadr)
                   if toadr > segend:   #not all data in segment
                       #print "out of segment"
                       catchlength = segend-fromadr
                   else:
                       catchlength = toadr-fromadr
                   #print toadr-fromadr
                   #print catchlength
                   res = res + seg.data[fromadr-seg.startaddress : fromadr-seg.startaddress+catchlength]
                   fromadr = fromadr + catchlength    #adjust start
                   if len(res) >= toadr-fromadr:
                       break#return res
           else:
                   res = res + b'\xff'
                   fromadr = fromadr + 1 #adjust start
                   #print "fill FF"
       #print "res: %r" % res
       return res

# shed skin: the following used to be BootStrapLoader class attributes 
ERR_VERIFY_FAILED       = "Error: verification failed"
ERR_ERASE_CHECK_FAILED  = "Error: erase check failed"

ACTION_PROGRAM          = 0x01 #Mask: program data
ACTION_VERIFY           = 0x02 #Mask: verify data
ACTION_ERASE_CHECK      = 0x04 #Mask: erase check

#Max. bytes sent within one frame if parsing a TI TXT file.
#( >= 16 and == n*16 and <= MAX_DATA_BYTES!)
MAXDATA                 = 240-16

#table with values from slaa089a.pdf
bauratetable = {
   F1x: {
        9600:[0x8580, 0x0000],
       19200:[0x86e0, 0x0001],
       38400:[0x87e0, 0x0002],
   },
   F4x: {
        9600:[0x9800, 0x0000],
       19200:[0xb000, 0x0001],
       38400:[0xc800, 0x0002],
   },
}

class BootStrapLoader(LowLevel):
   """higher level Bootstrap Loader functions."""

   # shed skin : change arguments
   #def __init__(self, *args, **kargs):
   #    LowLevel.__init__(self, *args, **kargs)
   def __init__(self):
       LowLevel.__init__(self) 
       self.byteCtr        = 0
       self.meraseCycles   = 1
       self.patchRequired  = 0
       self.patchLoaded    = 0
       self.bslVer         = 0
       self.passwd         = None
       self.data           = None
       self.maxData        = MAXDATA
       self.cpu            = None


   def preparePatch(self):
       """prepare to download patch"""
       if DEBUG > 1: sys.stderr.write("* preparePatch()\n")

       if self.patchLoaded:
           #Load PC with 0x0220.
           #This will invoke the patched bootstrap loader subroutines.
           self.bslTxRx(BSL_LOADPC,           #Command: Load PC
                          0x0220)                  #Address to load into PC
           self.BSLMemAccessWarning = 0 #Error is removed within workaround code
       return

   def postPatch(self):
       """setup after the patch is loaded"""
       if DEBUG > 1: sys.stderr.write("* postPatch()\n")
       if self.patchLoaded:
           self.BSLMemAccessWarning = 1                #Turn warning back on.


   def verifyBlk(self, addr, blkout, action):
       """verify memory against data or 0xff"""
       if DEBUG > 1: sys.stderr.write("* verifyBlk()\n")

       if action & ACTION_VERIFY or action & ACTION_ERASE_CHECK:
           if DEBUG: sys.stderr.write("  Check starting at 0x%04x, %d bytes ... \n" % (addr, len(blkout)))

           self.preparePatch()
           blkin = self.bslTxRx(BSL_RXBLK, addr, len(blkout))
           self.postPatch()

           for i in range(len(blkout)):
               if action & ACTION_VERIFY:
                   #Compare data in blkout and blkin
                   if blkin[i] != blkout[i]:
                       sys.stderr.write("Verification failed at 0x%04x (0x%02x, 0x%02x)\n" % (addr+i, blkin[i], blkout[i]))
                       sys.stderr.flush()
                       raise BSLException(ERR_VERIFY_FAILED)      #Verify failed!
                   continue
               elif action & ACTION_ERASE_CHECK:
                   #Compare data in blkin with erase pattern
                   if blkin[i] != 0xff:
                       sys.stderr.write("Erase Check failed at 0x%04x (0x%02x)\n" % (addr+i, blkin[i]))
                       sys.stderr.flush()
                       raise BSLException(ERR_ERASE_CHECK_FAILED) #Erase Check failed!
                   continue

   def programBlk(self, addr, blkout, action):
       """programm a memory block"""
       if DEBUG > 1: sys.stderr.write("* programBlk()\n")

       #Check, if specified range is erased
       self.verifyBlk(addr, blkout, action & ACTION_ERASE_CHECK)

       if action & ACTION_PROGRAM:
           if DEBUG: sys.stderr.write("  Program starting at 0x%04x, %i bytes ...\n" % (addr, len(blkout)))
           self.preparePatch()
           #Program block
           self.bslTxRx(BSL_TXBLK, addr, len(blkout), blkout)
           self.postPatch()

       #Verify block
       self.verifyBlk(addr, blkout, action & ACTION_VERIFY)

   #segments:
   #list of tuples or lists:
   #segements = [ (addr1, [d0,d1,d2,...]), (addr2, [e0,e1,e2,...])]
   def programData(self, segments, action): 
       """programm or verify data"""
       if DEBUG > 1: sys.stderr.write("* programData()\n")

       for seg in segments.segments: # shed skin : was : for seg in segments
           currentAddr = seg.startaddress
           pstart = 0
           while pstart<len(seg.data):
               length = MAXDATA
               if pstart+length > len(seg.data):
                   length = len(seg.data) - pstart
               self.programBlk(currentAddr, seg.data[pstart:pstart+length], action)
               pstart = pstart + length
               currentAddr = currentAddr + length
               self.byteCtr = self.byteCtr + length #total sum

   def uploadData(self, startaddress, size, wait=0):
       """upload a datablock"""
       if DEBUG > 1: sys.stderr.write("* uploadData()\n")
       data = b''
       pstart = 0
       while pstart<size:
           length = self.maxData
           if pstart+length > size:
               length = size - pstart
           data = data + self.bslTxRx(BSL_RXBLK,
                                      pstart+startaddress,
                                      length,
                                      wait=wait)[:-2] #cut away checksum
           pstart = pstart + length
       return data

   def txPasswd(self, passwd=None, wait=0):
       """transmit password, default if None is given."""
       if DEBUG > 1: sys.stderr.write("* txPassword(%r)\n" % passwd)
       if passwd is None:
           #Send "standard" password to get access to protected functions.
           sys.stderr.write("Transmit default password ...\n")
           sys.stderr.flush()
           #Flash is completely erased, the contents of all Flash cells is 0xff
           passwd = b'\xff'*32
       else:
           #sanity check of password
           if len(passwd) != 32:
               raise ValueError("password has wrong length (%d)\n" % len(passwd))
           sys.stderr.write('Transmit password ...\n')
           sys.stderr.flush()
       #send the password
       self.bslTxRx(BSL_TXPWORD,      #Command: Transmit Password
                      0xffe0,              #Address of interupt vectors
                      0x0020,              #Number of bytes
                      passwd,              #password
                      wait=wait)           #if wait is 1, try to sync forever


   #-----------------------------------------------------------------

   def actionMassErase(self):
       """Erase the flash memory completely (with mass erase command)"""
       sys.stderr.write("Mass Erase...\n")
       sys.stderr.flush()
       self.bslReset(1)                            #Invoke the boot loader.
       for i in range(self.meraseCycles):
           if i == 1: sys.stderr.write("Additional Mass Erase Cycles...\n")
           self.bslTxRx(BSL_MERAS,            #Command: Mass Erase
                               0xff00,             #Any address within flash memory.
                               0xa506)             #Required setting for mass erase!
       self.passwd = None                          #No password file required!
       #print "Mass Erase complete"
       #Transmit password to get access to protected BSL functions.
       self.txPasswd()

   # shed skin : change default None argument
   #def actionStartBSL(self, usepatch=1, adjsp=1, replacementBSL=None, forceBSL=0, mayuseBSL=0, speed=None, bslreset=1):
   def actionStartBSL(self, usepatch=1, adjsp=1, replacementBSL=None, forceBSL=0, mayuseBSL=0, speed=-1, bslreset=1):
       """start BSL, download patch if desired and needed, adjust SP if desired"""
       sys.stderr.write("Invoking BSL...\n")
       sys.stderr.flush()
       if bslreset:
           self.bslReset(1)                        #Invoke the boot loader.
       self.txPasswd(self.passwd)                  #transmit password

       #Read actual bootstrap loader version.
       #sys.stderr.write("Reading BSL version ...\n")
       blkin = self.bslTxRx(BSL_RXBLK,        #Command: Read/Receive Block
                         0x0ff0,                   #Start address
                         16)                       #No. of bytes to read
       dev_id, bslVerHi, bslVerLo = struct.unpack(">H8xBB4x", blkin[:-2]) #cut away checksum and extract data

       if self.cpu is None:                        #cpy type forced?
           if deviceids.has_key(dev_id):
               self.cpu = deviceids[dev_id]        #try to autodectect CPU type
               if DEBUG:
                   sys.stderr.write("Autodetect successful: %04x -> %s\n" % (dev_id, self.cpu))
           else:
               sys.stderr.write("Autodetect failed! Unkown ID: %04x. Trying to continue anyway.\n" % dev_id)
               self.cpu = F1x                      #assume something and try anyway..

       sys.stderr.write("Current bootstrap loader version: %x.%x (Device ID: %04x)\n" % (bslVerHi, bslVerLo, dev_id))
       sys.stderr.flush()
       self.bslVer = (bslVerHi << 8) | bslVerLo

       if self.bslVer <= 0x0110:                   #check if patch is needed
           self.BSLMemAccessWarning = 1
       else:
           self.BSLMemAccessWarning = 0 #Fixed in newer versions of BSL.

       if self.bslVer <= 0x0130 and adjsp:
           #only do this on BSL where it's needed to prevent
           #malfunction with F4xx devices/ newer ROM-BSLs

           #Execute function within bootstrap loader
           #to prepare stack pointer for the following patch.
           #This function will lock the protected functions again.
           sys.stderr.write("Adjust SP. Load PC with 0x0C22 ...\n")
           self.bslTxRx(BSL_LOADPC,           #Command: Load PC
                               0x0C22)             #Address to load into PC
           #Re-send password to re-gain access to protected functions.
           self.txPasswd(self.passwd)

       #get internal BSL replacement if needed or forced by the user
       #required if speed is set but an old BSL is in the device
       #if a BSL is given by the user, that one is used and not the internal one
       if ((mayuseBSL and speed and self.bslVer < 0x0150) or forceBSL) and replacementBSL is None:
           replacementBSL = Memory() #File to program
           if self.cpu == F4x:
               if DEBUG:
                   sys.stderr.write("Using built in BSL replacement for F4x devices\n")
                   sys.stderr.flush()
               replacementBSL.loadTIText(io.BytesIO(F4X_BSL))  #parse embedded BSL
           else:
               if DEBUG:
                   sys.stderr.write("Using built in BSL replacement for F1x devices\n")
                   sys.stderr.flush()
               replacementBSL.loadTIText(io.BytesIO(F1X_BSL))  #parse embedded BSL

       #now download the new BSL, if allowed and needed (version lower than the
       #the replacement) or forced
       if replacementBSL is not None:
           self.actionDownloadBSL(replacementBSL)

       #debug message with the real BSL version in use (may have changed after replacement BSL)
       if DEBUG:
           sys.stderr.write("Current bootstrap loader version: 0x%04x\n" % (self.bslVer,))
           sys.stderr.flush()

       #now apply workarounds or patches if BSL in use requires that
       if self.bslVer <= 0x0110:                   #check if patch is needed
           if usepatch:                            #test if patch is desired
               sys.stderr.write("Patch for flash programming required!\n")
               self.patchRequired = 1

               sys.stderr.write("Load and verify patch ...\n")
               sys.stderr.flush()
               #Programming and verification is done in one pass.
               #The patch file is only read and parsed once.
               segments = Memory()                     #data to program
               segments.loadTIText(io.BytesIO(PATCH))  #parse embedded patch
               #program patch
               self.programData(segments, ACTION_PROGRAM | ACTION_VERIFY)
               self.patchLoaded = 1
           else:
               if DEBUG:
                   sys.stderr.write("Device needs patch, but not applied (usepatch is false).\n")    #message if not patched

       #should the baudrate be changed?
       if speed != -1: # is not None # shed skin 
           self.actionChangeBaudrate(speed)            #change baudrate

   def actionDownloadBSL(self, bslsegments):
       sys.stderr.write("Load new BSL into RAM...\n")
       sys.stderr.flush()
       self.programData(bslsegments, ACTION_PROGRAM)
       sys.stderr.write("Verify new BSL...\n")
       sys.stderr.flush()
       self.programData(bslsegments, ACTION_VERIFY) #File to verify

       #Read startvector of bootstrap loader
       #blkin = self.bslTxRx(self.BSL_RXBLK, 0x0300, 2)
       #blkin = self.bslTxRx(self.BSL_RXBLK, 0x0220, 2)
       # shed skin : __getitem__ ?
       #blkin = self.bslTxRx(BSL_RXBLK, bslsegments[0].startaddress, 2)
       blkin = self.bslTxRx(BSL_RXBLK, bslsegments.segments[0].startaddress, 2)
       startaddr, = struct.unpack("<H", blkin[:2])

       sys.stderr.write("Starting new BSL at 0x%04x...\n" % startaddr)
       sys.stderr.flush()
       self.bslTxRx(BSL_LOADPC,  #Command: Load PC
                    startaddr)        #Address to load into PC

       #BSL-Bugs should be fixed within "new" BSL
       self.BSLMemAccessWarning = 0
       self.patchRequired = 0
       self.patchLoaded   = 0

       #Re-send password to re-gain access to protected functions.
       self.txPasswd(self.passwd)

       #update version info
       #verison only valid for the internal ones, but it also makes sure
       #that the patches are not applied if the user d/ls one
       self.bslVer = 0x0150

   def actionEraseCheck(self):
       """check the erasure of required flash cells."""
       sys.stderr.write("Erase Check by file ...\n")
       sys.stderr.flush()
       if self.data is not None:
           self.programData(self.data, ACTION_ERASE_CHECK)
       else:
           raise BSLException("cannot do erase check against data with not knowing the actual data")

   def actionProgram(self):
       """program data into flash memory."""
       if self.data is not None:
           sys.stderr.write("Program ...\n")
           sys.stderr.flush()
           self.programData(self.data, ACTION_PROGRAM)
           sys.stderr.write("%i bytes programmed.\n" % self.byteCtr)
           sys.stderr.flush()
       else:
           raise BSLException("programming without data not possible")

   def actionVerify(self):
       """Verify programmed data"""
       if self.data is not None:
           sys.stderr.write("Verify ...\n")
           sys.stderr.flush()
           self.programData(self.data, ACTION_VERIFY)
       else:
           raise BSLException("verify without data not possible")

   def actionReset(self):
       """perform a reset, start user programm"""
       sys.stderr.write("Reset device ...\n")
       sys.stderr.flush()
       self.bslReset(0) #only reset

   def actionRun(self, address=0x220):
       """start program at specified address"""
       sys.stderr.write("Load PC with 0x%04x ...\n" % address)
       sys.stderr.flush()
       self.bslTxRx(BSL_LOADPC, #Command: Load PC
                           address)  #Address to load into PC

   def actionChangeBaudrate(self, baudrate=9600):
       """change baudrate. first the command is sent, then the comm
       port is reprogrammed. only possible with newer MSP430-BSL versions.
       (ROM >=1.6, downloadable >=1.5)"""
       try:
           baudconfigs = bauratetable[self.cpu]
       except KeyError:
           raise ValueError("unknown CPU type %s, can't switch baudrate" % self.cpu)
       try:
           a,l = baudconfigs[baudrate]
       except KeyError:
           raise ValueError("baudrate not valid. valid values are %r" % baudconfigs.keys())
       #a, l = 0x87e0, 0x0002

       sys.stderr.write("Changing baudrate to %d ...\n" % baudrate)
       sys.stderr.flush()
       self.bslTxRx(BSL_CHANGEBAUD,   #Command: change baudrate
                   a, l)                   #args are coded in adr and len
       time.sleep(0.010)                   #recomended delay
       self.serialport.setBaudrate(baudrate)

   def actionReadBSLVersion(self):
       """informational output of BSL version number.
       (newer MSP430-BSLs only)"""
       ans = self.bslTxRx(BSL_TXVERSION, 0) #Command: receive version info
       #the following values are in big endian style!!!
       family_type, bsl_version = struct.unpack(">H8xH4x", ans[:-2]) #cut away checksum and extract data
       print("Device Type: 0x%04x\nBSL version: 0x%04x\n" % (family_type, bsl_version))


def usage():
   """print some help message"""
   sys.stderr.write("""
USAGE: %s [options] [file]
Version: %s

If "-" is specified as file the data is read from the stdinput.
A file ending with ".txt" is considered to be in TIText format,
'.a43' and '.hex' as IntelHex and all other filenames are
considered as ELF files.

General options:
 -h, --help            Show this help screen.
 -c, --comport=port    Specify the communication port to be used.
                       (Default is 0)
                               0->COM1 / ttyS0
                               1->COM2 / ttyS1
                               etc.
 -P, --password=file   Specify a file with the interrupt vectors that
                       are used as password. This can be any file that
                       has previously been used to program the device.
                       (e.g. -P INT_VECT.TXT).
 -f, --framesize=num   Max. number of data bytes within one transmitted
                       frame (16 to 240 in steps of 16) (e.g. -f 240).
 -m, --erasecycles=num Number of mass erase cycles (default is 1). Some
                       old F149 devices need additional erase cycles.
                       On newer devices it is no longer needed. (e.g. for
                       an old F149: -m20)
 -U, --unpatched       Do not download the BSL patch, even when it is
                       needed. This is used when a program is downloaded
                       into RAM and executed from there (and where flash
                       programming is not needed.)
 -D, --debug           Increase level of debug messages. This won't be
                       very useful for the average user...
 -I, --intelhex        Force fileformat to IntelHex
 -T, --titext          Force fileformat to be TIText
 -N, --notimeout       Don't use timeout on serial port (use with care)
 -B, --bsl=bsl.txt     Load and use new BSL from the TI Text file
 -S, --speed=baud      Reconfigure speed, only possible with newer
                       MSP403-BSL versions (>1.5, read slaa089a.pdf for
                       details). If the --bsl option is not used, an
                       internal BSL replacement will be loaded.
                       Needs a target with at least 2kB RAM!
                       Possible values are 9600, 19200, 38400
                       (default 9600)
 -1, --f1x             Specify CPU family, in case autodetect fails
 -4, --f4x             Specify CPU family, in case autodetect fails
                       --F1x and --f2x are only needed when the "change
                       baudrate" feature is used and the autodetect feature
                       fails. If the device ID that is uploaded is known, it
                       has precedence to the command line option.
 --invert-reset        Invert signal on RST pin (used for some BSL hardware)
 --invert-test         Invert signal on TEST/TCK pin (used for some BSL
                       hardware)
 --swap-reset-test     Swap the RST and TEST pins (used for some BSL hardware)
 --telos-latch         Special twiddle in BSL reset for Telos hardware
 --telos-i2c           DTR/RTS map via an I2C switch to TCK/RST in Telos Rev.B
 --telos               Implies options --invert-reset, --invert-test,
                       --swap-reset-test, and --telos-latch
 --telosb              Implies options --swap-reset-test, --telos-i2c,
                       --no-BSL-download, and --speed=38400
 --tmote               Identical operation to --telosb
 --no-BSL-download     Do not download replacement BSL (disable automatic)
 --force-BSL-download  Download replacement BSL even if not needed (the one
                       in the device would have the required features)
 --slow                Add delays when operating the conrol pins. Useful if
                       the pins/circuit has high capacitance.

Program Flow Specifiers:
 -e, --masserase       Mass Erase (clear all flash memory)
 -E, --erasecheck      Erase Check by file
 -p, --program         Program file
 -v, --verify          Verify by file

The order of the above options matters! The table is ordered by normal
execution order. For the options "Epv" a file must be specified.
Program flow specifiers default to "pvr" if a file is given.
Don't forget to specify "e" or "eE" when programming flash!

Data retreiving:
 -u, --upload=addr     Upload a datablock (see also: -s).
 -s, --size=num        Size of the data block do upload. (Default is 2)
 -x, --hex             Show a hexadecimal display of the uploaded data.
                       (Default)
 -b, --bin             Get binary uploaded data. This can be used
                       to redirect the output into a file.

Do before exit:
 -g, --go=address      Start programm execution at specified address.
                       This implies option --wait.
 -r, --reset           Reset connected MSP430. Starts application.
                       This is a normal device reset and will start
                       the programm that is specified in the reset
                       vector. (see also -g)
 -w, --wait            Wait for <ENTER> before closing serial port.

If it says "NAK received" it's probably because you specified no or a
wrong password.
""" % (sys.argv[0], VERSION))

# shed skin : too dynamic, and not used
#add some arguments to a function, but don't call it yet, instead return
#a wrapper object for later invocation
#class curry:
#   """create a callable with some arguments specified in advance"""
#   def __init__(self, fun, *args, **kwargs):
#       self.fun = fun
#       self.pending = args[:]
#       self.kwargs = kwargs.copy()
#
#   def __call__(self, *args, **kwargs):
#       if kwargs and self.kwargs:
#           kw = self.kwargs.copy()
#           kw.update(kwargs)
#       else:
#           kw = kwargs or self.kwargs
#       return apply(self.fun, self.pending + args, kw)
#
#   def __repr__(self):
#       #first try if it a function
#       try:
#           return "curry(%s, %r, %r)" % (self.fun.func_name, self.pending, self.kwargs)
#       except AttributeError:
#           #fallback for callable classes
#           return "curry(%s, %r, %r)" % (self.fun, self.pending, self.kwargs)

def hexify(line, bytes, width=16):
   # shed skin : lh-strings in % operation must be constant
   bytestr = ''.join([('%02x ' % b) for b in bytes])
   charstr = ''
   for b in bytes:
       if b>=32 and b<127: charstr += chr(b)
       else: charstr += '.'

   return  '%04x  %s%s %s' % (
       line,
       #('%02x '*len(bytes)) % tuple(bytes),
       bytestr,
       '   '* (width-len(bytes)),
       #('%c'*len(bytes)) % tuple(map(lambda x: (x>=32 and x<127) and x or ord('.'), bytes))
       charstr,
       )

#Main:
def main():
   global DEBUG
   #import getopt # shed skin : move to top
   filetype    = -1 # shed skin (was None)
   filename    = None
   comPort     = None     #Default setting. # shed skin : always str
   speed       = -1 # shed skin (was None)
   unpatched   = 0
   reset       = 0
   wait        = 0     #wait at the end
   goaddr      = -1 # shed skin (was None)
   bsl         = BootStrapLoader()

   #toinit      = [] # shed skin: too dynamic
   toinit = 0
   toinit_actionMassErase = 0
   toinit_actionEraseCheck = 0
   #todo        = [] # shed skin: too dynamic
   todo = 0
   todo_actionProgram = 0
   todo_actionVerify = 0
   todo_actionReadBSLVersion = 0

   startaddr   = -1 # shed skin (was None)
   size        = 2
   hexoutput   = 1
   notimeout   = 0
   bslrepl     = None
   mayuseBSL   = 1
   forceBSL    = 0

   sys.stderr.write("MSP430 Bootstrap Loader Version: %s\n" % VERSION)

   try:
       opts, args = getopt.getopt(sys.argv[1:],
           "hc:P:wf:m:eEpvrg:UDudsxbITNB:S:V14",
           ["help", "comport=", "password=", "wait", "framesize=",
            "erasecycles=", "masserase", "erasecheck", "program",
            "verify", "reset", "go=", "unpatched", "debug",
            "upload=", "download=", "size=", "hex", "bin",
            "intelhex", "titext", "notimeout", "bsl=", "speed=",
            "bslversion", "f1x", "f4x", "invert-reset", "invert-test",
            "swap-reset-test", "telos-latch", "telos-i2c", "telos", "telosb",
            "tmote","no-BSL-download", "force-BSL-download", "slow"]
       )
   except getopt.GetoptError:
       # print help information and exit:
       usage()
       sys.exit(2)

   for o, a in opts:
       if o in ("-h", "--help"):
           usage()
           sys.exit()
       elif o in ("-c", "--comport"):
# shed skin 
#           try:
#               comPort = int(a)                    #try to convert decimal
#           except ValueError:
               comPort = a                         #take the string and let serial driver decide
       elif o in ("-P", "--password"):
           #extract password from file
           bsl.passwd = Memory(a).getMemrange(0xffe0, 0xffff)
       elif o in ("-w", "--wait"):
           wait = 1
       elif o in ("-f", "--framesize"):
           try:
               maxData = int(a)                    #try to convert decimal
           except ValueError:
               sys.stderr.write("framesize must be a valid number\n")
               sys.exit(2)
           #Make sure that conditions for maxData are met:
           #( >= 16 and == n*16 and <= MAX_DATA_BYTES!)
           if maxData > MAX_DATA_BYTES: 
               maxData = MAX_DATA_BYTES
           elif maxData < 16:
               maxData = 16
           bsl.maxData = maxData - (maxData % 16)
           sys.stderr.write( "Max. number of data bytes within one frame set to %i.\n" % maxData)
       elif o in ("-m", "--erasecycles"):
           try:
               meraseCycles = int(a)               #try to convert decimal
           except ValueError:
               sys.stderr.write("erasecycles must be a valid number\n")
               sys.exit(2)
           #sanity check of value
           if meraseCycles < 1:
               sys.stderr.write("erasecycles must be a positive number\n")
               sys.exit(2)
           if meraseCycles > 20:
               sys.stderr.write("warning: erasecycles set to a large number (>20): %d\n" % meraseCycles)
           sys.stderr.write( "Number of mass erase cycles set to %i.\n" % meraseCycles)
           bsl.meraseCycles = meraseCycles
       elif o in ("-e", "--masserase"):
#           toinit.append(bsl.actionMassErase)        #Erase Flash
          toinit = toinit_actionMassErase = 1
       elif o in ("-E", "--erasecheck"):
#           toinit.append(bsl.actionEraseCheck)       #Erase Check (by file)
          toinit = toinit_actionEraseCheck = 1
       elif o in ("-p", "--programm"):
#           todo.append(bsl.actionProgram)          #Program file
           todo = todo_actionProgram = 1
       elif o in ("-v", "--verify"):
#           todo.append(bsl.actionVerify)           #Verify file
           todo = todo_actionVerify = 1
       elif o in ("-r", "--reset"):
           reset = 1
       elif o in ("-g", "--go"):
           try:
               goaddr = int(a)                    #try to convert decimal
           except ValueError:
               try:
                   goaddr = int(a[2:],16)         #try to convert hex
               except ValueError:
                   sys.stderr.write("go address must be a valid number\n")
                   sys.exit(2)
           wait = 1
       elif o in ("-U", "--unpatched"):
           unpatched = 1
       elif o in ("-D", "--debug"):
           DEBUG = DEBUG + 1
       elif o in ("-u", "--upload"):
           try:
               startaddr = int(a)                  #try to convert decimal
           except ValueError:
               try:
                   startaddr = int(a,16)           #try to convert hex
               except ValueError:
                   sys.stderr.write("upload address must be a valid number\n")
                   sys.exit(2)
       elif o in ("-s", "--size"):
           try:
               size = int(a)
           except ValueError:
               try:
                   size = int(a,16)
               except ValueError:
                   sys.stderr.write("size must be a valid number\n")
                   sys.exit(2)
       elif o in ("-x", "--hex"):
           hexoutput = 1
       elif o in ("-b", "--bin"):
           hexoutput = 0
       elif o in ("-I", "--intelhex"):
           filetype = 0
       elif o in ("-T", "--titext"):
           filetype = 1
       elif o in ("-N", "--notimeout"):
           notimeout = 1
       elif o in ("-B", "--bsl"):
           bslrepl = Memory() #File to program
           bslrepl.loadFile(a)
       elif o in ("-V", "--bslversion"):
#           todo.append(bsl.actionReadBSLVersion) #load replacement BSL as first item
           todo = todo_actionReadBSLVersion = 1
       elif o in ("-S", "--speed"):
           try:
               speed = int(a)                    #try to convert decimal
           except ValueError:
               sys.stderr.write("speed must be decimal number\n")
               sys.exit(2)
       elif o in ("-1", "--f1x"):
           bsl.cpu = F1x
       elif o in ("-4", "--f4x"):
           bsl.cpu = F4x
       elif o in ("--invert-reset", ):
           bsl.invertRST = 1
       elif o in ("--invert-test", ):
           bsl.invertTEST = 1
       elif o in ("--swap-reset-test", ):
           bsl.swapRSTTEST = 1
       elif o in ("--telos-latch", ):
           bsl.telosLatch = 1
       elif o in ("--telos-i2c", ):
           bsl.telosI2C = 1
       elif o in ("--telos", ):
           bsl.invertRST = 1
           bsl.invertTEST = 1
           bsl.swapRSTTEST = 1
           bsl.telosLatch = 1
       elif o in ("--telosb", ):
           bsl.swapRSTTEST = 1
           bsl.telosI2C = 1
           mayuseBSL = 0
           speed = 38400
       elif o in ("--tmote", ):
           bsl.swapRSTTEST = 1
           bsl.telosI2C = 1
           mayuseBSL = 0
           speed = 38400
       elif o in ("--no-BSL-download", ):
           mayuseBSL = 0
       elif o in ("--force-BSL-download", ):
           forceBSL = 1
       elif o in ("--slow", ):
           bsl.slowmode = 1

   if len(args) == 0:
       sys.stderr.write("Use -h for help\n")
   elif len(args) == 1:                            #a filename is given
       if not todo:                                #if there are no actions yet
           todo = todo_actionProgram = 1
           todo = todo_actionVerify = 1
#           todo.extend([                           #add some useful actions...
#               bsl.actionProgram,
#               bsl.actionVerify,
#           ])
       filename = args[0]
   else:                                           #number of args is wrong
       usage()
       sys.exit(2)

   # shed skin
   if comPort is None:
       sys.stderr.write("No comport specified\n")
       sys.exit()

   if DEBUG:   #debug infos
       sys.stderr.write("Debug level set to %d\n" % DEBUG)
       sys.stderr.write("Python version: %s\n" % sys.version)

   #sanity check of options
   if notimeout and goaddr != -1 and startaddr != -1:
       sys.stderr.write("Option --notimeout can not be used together with both --upload and --go\n")
       sys.exit(1)

   if notimeout:
       sys.stderr.write("Warning: option --notimeout can cause improper function in some cases!\n")
       bsl.timeout = 0

   if goaddr != -1 and reset:
       sys.stderr.write("Warning: option --reset ignored as --go is specified!\n")
       reset = 0

   if startaddr != -1 and reset:
       sys.stderr.write("Warning: option --reset ignored as --upload is specified!\n")
       reset = 0

   sys.stderr.flush()

   #prepare data to download
   bsl.data = Memory()                             #prepare downloaded data
   # shed skin : != -1
   if filetype != -1: #is not None:                        #if the filetype is given...
       if filename is None:
           raise ValueError("no filename but filetype specified")
       if filename == '-':                         #get data from stdin
           pass #file = sys.stdin
       else:
           file = open(filename, "rb")             #or from a file
       if filetype == 0:                           #select load function
           bsl.data.loadIHex(file)
       elif filetype == 1:
           bsl.data.loadTIText(file)               #TI's format
       else:
           raise ValueError("illegal filetype specified")
   else:                                           #no filetype given...
       if filename == '-':                         #for stdin:
           pass #bsl.data.loadIHex(sys.stdin)            #assume intel hex
       elif filename:
           bsl.data.loadFile(filename)             #autodetect otherwise

   if DEBUG > 3: sys.stderr.write("File: %r" % filename)

   bsl.comInit(comPort)                            #init port

   #initialization list
   if toinit:  #erase and erase check
       if DEBUG: sys.stderr.write("Preparing device ...\n")
       #bsl.actionStartBSL(usepatch=0, adjsp=0)     #no workarounds needed
       #if speed: bsl.actionChangeBaudrate(speed)   #change baud rate as fast as possible
       #for f in toinit: f()
       if toinit_actionMassErase: bsl.actionMassErase()
       if toinit_actionEraseCheck: bsl.actionEraseCheck()
           
   if todo or goaddr != -1 or startaddr != -1:
       if DEBUG: sys.stderr.write("Actions ...\n")
       #connect to the BSL
       bsl.actionStartBSL(1-unpatched, 1, bslrepl, forceBSL, mayuseBSL, speed, 1)
#       bsl.actionStartBSL(
#           usepatch=not unpatched,
#           replacementBSL=bslrepl,
#           forceBSL=forceBSL,
#           mayuseBSL=mayuseBSL,
#           speed=speed,
#       )

   #work list
   if todo:
#       if DEBUG > 0:       #debug
#           #show a nice list of sheduled actions
#           sys.stderr.write("TODO list:\n")
#           for f in todo:
#               try:
#                   sys.stderr.write("   %s\n" % f.func_name)
#               except AttributeError:
#                   sys.stderr.write("   %r\n" % f)
#       for f in todo: f()                          #work through todo list
       if todo_actionProgram: bsl.actionProgram()
       if todo_actionVerify: bsl.actionVerify()
       if todo_actionReadBSLVersion: bsl.actionReadBSLVersion()
           

   if reset:                                       #reset device first if desired
       bsl.actionReset()

   if goaddr != -1:                          #start user programm at specified address
       bsl.actionRun(goaddr)                       #load PC and execute

   #upload datablock and output
   if startaddr != -1: 
       if goaddr != -1:                                  #if a program was started...
           #don't restart BSL but wait for the device to enter it itself
           sys.stderr.write("Waiting for device to reconnect for upload: ")
           sys.stderr.flush()
           bsl.txPasswd(bsl.passwd, wait=1)        #synchronize, try forever...
           data = bsl.uploadData(startaddr, size)  #upload data
       else:
           data = bsl.uploadData(startaddr, size)  #upload data
       if hexoutput:                               #depending on output format
           m = 0
           while m < len(data):                    #print a hex display
               print(hexify(startaddr+m, data[m:m+16]))
               m = m + 16
       else:
           sys.stdout.write(str(data))                  #binary output w/o newline!
       wait = 0    #wait makes no sense as after the upload the device is still in BSL

   if wait:                                        #wait at the end if desired
       sys.stderr.write("Press <ENTER> ...\n")     #display a prompt
       sys.stderr.flush()
       input()                                 #wait for newline


   bsl.comDone()           #Release serial communication port

# shed skin
if __name__ == '__main__':
#try:
   main()
# shed skin
#   except SystemExit:
#       raise               #let pass exit() calls
#   except KeyboardInterrupt:
#       if DEBUG: raise     #show full trace in debug mode
#       sys.stderr.write("user abort.\n")   #short messy in user mode
#       sys.exit(1)         #set errorlevel for script usage
#except Exception, msg:  #every Exception is caught and displayed
##   if DEBUG: raise     #show full trace in debug mode
#   sys.stderr.write("\nAn error occoured:\n%s\n" % msg) #short messy in user mode
#   sys.exit(1)         #set errorlevel for script usage


