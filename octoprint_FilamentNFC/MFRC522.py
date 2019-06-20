#!/usr/bin/env python
# -*- coding: utf8 -*-
#
#    Copyright 2014,2018 Mario Gomez <mario.gomez@teubi.co>
#
#    This file is part of MFRC522-Python
#    MFRC522-Python is a simple Python implementation for
#    the MFRC522 NFC Card Reader for the Raspberry Pi.
#
#    MFRC522-Python is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    MFRC522-Python is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with MFRC522-Python.  If not, see <http://www.gnu.org/licenses/>.
#

import RPi.GPIO as GPIO
import spidev
import signal
import time


#*************SAK & ATQA**************
# MIFARE:
# Mini      = 09  00 04  UID - 4 bytes
# Clssic 1K = 08  00 04  UID - 4 bytes
# Clssic 4K = 18  00 02  UID - 4 bytes
# Ultalight = 00  00 44  UID - 7 bytes
# Plus      = 20  00 44  UID - 7 bytes
#*************************************

MIFARE_CLASSIC_1K_KEYS = [
    [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF],
    [0x00, 0x11, 0x22, 0x33, 0x44, 0x55],
    [0x00, 0x01, 0x02, 0x03, 0x04, 0x05],
    [0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5],
    [0xB0, 0xB1, 0xB2, 0xB3, 0xB4, 0xB5],
    [0xAA, 0xAA, 0xAA, 0xAA, 0xAA, 0xAA],
    [0xBB, 0xBB, 0xBB, 0xBB, 0xBB, 0xBB],
    [0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF],
    [0XD3, 0XF7, 0XD3, 0XF7, 0XD3, 0XF7],
    [0XB0, 0XB1, 0XB2, 0XB3, 0XB4, 0XB5],
    [0X4D, 0X3A, 0X99, 0XC3, 0X51, 0XDD],
    [0X1A, 0X98, 0X2C, 0X7E, 0X45, 0X9A],
    [0X00, 0X00, 0X00, 0X00, 0X00, 0X00],
    [0XAB, 0XCD, 0XEF, 0X12, 0X34, 0X56]
]

spi=spidev.SpiDev()
  
class MFRC522:
    NRSTPD  = 22

    MAX_LEN = 16
    # CommandReg:
    CR_POWERDOWN      = 0x10    #  Soft power-down mode entered
    CR_RCVOFF         = 0x20    # analog part of the receiver is switched off
    # CommandReg -> command (Proximity Coupling Device)
    PCD_IDLE          = 0x00    # no action, cancels current command execution
    PCD_MEM           = 0x01    # stores 25 bytes into the internal buffer
    PCD_GENRENDID     = 0x02    # generates a 10-byte random ID number
    PCD_CALCCRC       = 0x03    # activates the CRC coprocessor or performs a self test
    PCD_TRANSMIT      = 0x04    # transmits data from the FIFO buffer
    PCD_NOCMDCHANGE   = 0x07    # no command change, can be used to modify the CommandReg register bits without affecting the command, for example, the PowerDown bit
    PCD_RECEIVE       = 0x08    # activates the receiver circuits
    PCD_TRANSCEIVE    = 0x0C    # transmits data from FIFO buffer to antenna and automatically activates the receiver after transmission
    PCD_RESERVED      = 0x0D
    PCD_AUTHENT       = 0x0E    # performs the MIFARE standard authentication as a reader
    PCD_RESETPHASE    = 0x0F    # resets the MFRC522
    # RFCfgReg:
    RFC_RXGAIN18dB    = 0x00
    RFC_RXGAIN23dB    = 0x10
    RFC_RXGAIN33dB    = 0x40
    RFC_RXGAIN38dB    = 0x50
    RFC_RXGAIN43dB    = 0x60
    RFC_RXGAIN48dB    = 0x70
    #ISO/IEC 14443 commands (Proximity Integrated Circuit)
    PICC_REQIDL       = 0x26    # Request (REQA)
    PICC_REQALL       = 0x52    # Wake-up (WUPA)
    PICC_ANTICOLL1    = 0x93    # Anticollision CL1
    PICC_ANTICOLL2    = 0x95    # Anticollision CL2
    PICC_ANTICOLL3    = 0x97    # Anticollision CL3
    PICC_SElECTTAG1   = 0x93    # Select CL1
    PICC_SElECTTAG2   = 0x95    # Select CL2
    PICC_SElECTTAG3   = 0x97    # Select CL3
    PICC_AUTHENT1A    = 0x60    # Authentication with Key A
    PICC_AUTHENT1B    = 0x61    # Authentication with Key B
    PICC_PERSONUIDUSE = 0x40    # Personalize UID Usage
    PICC_SETMODTYPE   = 0x43    # SET_MOD_TYPE
    PICC_READ         = 0x30    # MIFARE Read
    PICC_WRITE        = 0xA0    # MIFARE Write
    PICC_DECREMENT    = 0xC0    # MIFARE Decrement
    PICC_INCREMENT    = 0xC1    # MIFARE Increment
    PICC_RESTORE      = 0xC2    # MIFARE Restore
    PICC_TRANSFER     = 0xB0    # MIFARE Transfer
    PICC_HALT         = 0x50    # Halt

    PICC_ANTICOLL     = [PICC_ANTICOLL1,PICC_ANTICOLL2,PICC_ANTICOLL3]
    PICC_SElECTTAG    = [PICC_SElECTTAG1,PICC_SElECTTAG2,PICC_SElECTTAG3]

    MI_OK             = 0
    MI_NOTAGERR       = 1
    MI_ERR            = 2
    # Command and status:
    Reserved00        = 0x00
    CommandReg        = 0x01    # Starts and stops command execution
    CommIEnReg        = 0x02    # Enable and disable interrupt request control bits
    DivlEnReg         = 0x03    # enable and disable interrupt request control bits
    CommIrqReg        = 0x04    # interrupt request bits
    DivIrqReg         = 0x05    # interrupt request bits
    ErrorReg          = 0x06    # error bits showing the error status of the last command executed
    Status1Reg        = 0x07    # communication status bits
    Status2Reg        = 0x08    # receiver and transmitter status bits
    FIFODataReg       = 0x09    # input and output of 64 byte FIFO buffer
    FIFOLevelReg      = 0x0A    # number of bytes stored in the FIFO buffer
    WaterLevelReg     = 0x0B    # level for FIFO underflow and overflow warning
    ControlReg        = 0x0C    # miscellaneous control registers
    BitFramingReg     = 0x0D    # adjustments for bit-oriented frames
    CollReg           = 0x0E    # bit position of the first bit-collision detected on the RF interface
    Reserved01        = 0x0F
    # Command:
    Reserved10        = 0x10
    ModeReg           = 0x11    # defines general modes for transmitting and receiving
    TxModeReg         = 0x12    # defines transmission data rate and framing
    RxModeReg         = 0x13    # defines reception data rate and framing
    TxControlReg      = 0x14    # controls the logical behavior of the antenna driver pins TX1 and TX2
    TxASKReg          = 0x15    # controls the setting of the transmission modulation
    TxSelReg          = 0x16    # selects the internal sources for the antenna driver
    RxSelReg          = 0x17    # selects internal receiver settings
    RxThresholdReg    = 0x18    # selects thresholds for the bit decoder
    DemodReg          = 0x19    # defines demodulator settings
    Reserved11        = 0x1A
    Reserved12        = 0x1B
    MfTxReg           = 0x1C    # controls some MIFARE communication transmit parameters
    MfRxReg           = 0x1D    # controls some MIFARE communication receive parameters
    Reserved14        = 0x1E
    SerialSpeedReg    = 0x1F    #  selects the speed of the serial UART interface
    # Configuration:
    Reserved20        = 0x20
    CRCResultRegM     = 0x21    # shows the MSB values of the CRC calculation
    CRCResultRegL     = 0x22    # shows the LSB values of the CRC calculation
    Reserved21        = 0x23
    ModWidthReg       = 0x24    # controls the ModWidth setting
    Reserved22        = 0x25
    RFCfgReg          = 0x26    # configures the receiver gain
    GsNReg            = 0x27    # selects the conductance of the antenna driver pins TX1 and TX2 for modulation
    CWGsPReg          = 0x28    # defines the conductance of the p-driver output during periods of no modulation
    ModGsPReg         = 0x29    # defines the conductance of the p-driver output during periods of modulation
    TModeReg          = 0x2A    # defines settings for the internal timer
    TPrescalerReg     = 0x2B    # defines settings for the internal timer
    TReloadRegH       = 0x2C    # defines the 16-bit timer reload value
    TReloadRegL       = 0x2D    # defines the 16-bit timer reload value
    TCounterValueRegH = 0x2E    # shows the 16-bit timer value
    TCounterValueRegL = 0x2F    # shows the 16-bit timer value
    # Test register:
    Reserved30        = 0x30
    TestSel1Reg       = 0x31    # general test signal configuration
    TestSel2Reg       = 0x32    # general test signal configuration and PRBS control
    TestPinEnReg      = 0x33    # enables pin output driver on pins D1 to D7
    TestPinValueReg   = 0x34    # defines the values for D1 to D7 when it is used as an I/O bus Ta
    TestBusReg        = 0x35    # shows the status of the internal test bus
    AutoTestReg       = 0x36    # controls the digital self test
    VersionReg        = 0x37    # shows the software version
    AnalogTestReg     = 0x38    # controls the pins AUX1 and AUX2
    TestDAC1Reg       = 0x39    # defines the test value for TestDAC1
    TestDAC2Reg       = 0x3A    # defines the test value for TestDAC2
    TestADCReg        = 0x3B    #  shows the value of ADC I and Q channels
    Reserved31        = 0x3C
    Reserved32        = 0x3D
    Reserved33        = 0x3E
    Reserved34        = 0x3F

    mifareUltralight  = 1
    mifareClassic1K   = 2
    mifareClassic2K   = 3
    mifareClassic4K   = 4
    
    mifareATQA = [0x0000,0x0044,0x0004,0x0005,0x0002]
    mifareName = ['None','Ultralight','Clssic 1K','Clssic 2K','Classic4K']

    SAK     = 0
    ATQA    = 0
    
    #ISO/IEC 14443-3: Table 9 — Coding of SAK:
    ATQA_UIDSINGLE = 0x0000     # 4 bytes (CL1)
    ATQA_UIDDOUBLE = 0x0040     # 7 bytes (CL2)
    ATQA_UIDTRIPLE = 0x0080     # 10 bytes (CL3)
    ATQA_UIDMASK   = 0x00C0
    
    
    
    tagType      = 0
    tagAuth      = 0
    uidLen       = 4
    cascadeLevel = 1
    
    DEBUG = 1
#******************************************************************************************
#******************************************************************************************
#******************************************************************************************
    def __init__(self, dev=0, spd=1000000, bus=0):
        spi.open(dev,bus)
        spi.max_speed_hz = spd
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.NRSTPD, GPIO.OUT)
        GPIO.output(self.NRSTPD, 1)
        self.MFRC522_Init()
#******************************************************************************************
    def mifareCardSelect(self, SAK):     # See AN10834 "MIFARE ISO/IEC 14443 PICC Selection"
        type = 0
        auth = 0
        if (SAK == 0x00):
            type = self.mifareUltralight
            auth = 0
        if (SAK == 0x08):
            type = self.mifareClassic1K
            auth = 1
        if (SAK == 0x19):
            type = self.mifareClassic2K
            auth = 1
        if (SAK == 0x18):
            type = self.mifareClassic4K
            auth = 1
        if (self.DEBUG):
            print ">>Mifare type = "+self.mifareName[type]
            print ">>Authication = "+str(auth)
        return (type,auth)
#******************************************************************************************
    def MFRC522_Reset(self):
        self.Write_MFRC522(self.CommandReg, self.PCD_RESETPHASE)
#******************************************************************************************
    def Write_MFRC522(self, addr, val):
        spi.xfer2(((addr<<1)&0x7E,val))
#******************************************************************************************
    def Read_MFRC522(self, addr):
        val = spi.xfer2((((addr<<1)&0x7E) | 0x80,0))
        return val[1]
#******************************************************************************************
    def SetBitMask(self, reg, mask):
        tmp = self.Read_MFRC522(reg)
        self.Write_MFRC522(reg, tmp | mask)
#******************************************************************************************
    def ClearBitMask(self, reg, mask):
        tmp = self.Read_MFRC522(reg);
        self.Write_MFRC522(reg, tmp & (~mask))
#******************************************************************************************
    def AntennaOn(self):
        temp = self.Read_MFRC522(self.TxControlReg)
        if(~(temp & 0x03)):
            self.SetBitMask(self.TxControlReg, 0x03)
#******************************************************************************************
    def AntennaOff(self):
        self.ClearBitMask(self.TxControlReg, 0x03)
#******************************************************************************************
    def MFRC522_ToCard(self,command,sendData):
        backData = []
        backLen  = 0
        status   = self.MI_ERR
        irqEn    = 0x00
        waitIRq  = 0x00
        lastBits = None
        n = 0
        i = 0
        if command == self.PCD_AUTHENT:
            irqEn   = 0x12
            waitIRq = 0x10
        if command == self.PCD_TRANSCEIVE:
            irqEn   = 0x77
            waitIRq = 0x30
        self.Write_MFRC522(self.CommIEnReg, irqEn|0x80)
        self.ClearBitMask(self.CommIrqReg, 0x80)
        self.SetBitMask(self.FIFOLevelReg, 0x80)
        self.Write_MFRC522(self.CommandReg, self.PCD_IDLE);
        while(i<len(sendData)):
            self.Write_MFRC522(self.FIFODataReg, sendData[i])
            i = i+1
        self.Write_MFRC522(self.CommandReg, command)
        if command == self.PCD_TRANSCEIVE:
            self.SetBitMask(self.BitFramingReg, 0x80)
        i = 2000
        while True:
            n = self.Read_MFRC522(self.CommIrqReg)
            i = i - 1
            if ~((i!=0) and ~(n&0x01) and ~(n&waitIRq)):
                break
        self.ClearBitMask(self.BitFramingReg, 0x80)
        if i != 0:
            if (self.Read_MFRC522(self.ErrorReg) & 0x1B)==0x00:
                status = self.MI_OK
            if n & irqEn & 0x01:
                status = self.MI_NOTAGERR
            if command == self.PCD_TRANSCEIVE:
                n = self.Read_MFRC522(self.FIFOLevelReg)
                lastBits = self.Read_MFRC522(self.ControlReg) & 0x07
                if lastBits != 0:
                    backLen = (n-1)*8 + lastBits
                else:
                    backLen = n*8
                if n == 0:
                    n = 1
                if n > self.MAX_LEN:
                    n = self.MAX_LEN
                i = 0
                while i<n:
                    backData.append(self.Read_MFRC522(self.FIFODataReg))
                    i = i + 1;
        else:
            status = self.MI_ERR
        return (status,backData,backLen)
#******************************************************************************************
#
# Request give back backData too
#
    def MFRC522_Request(self, reqMode):
        if (self.DEBUG):
            print ">>------REQUEST------"
        status   = None
        backBits = None
        TagType  = []
        self.Write_MFRC522(self.BitFramingReg, 0x07)
        TagType.append(reqMode);
        (status,backData,backBits) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, TagType)
        if (status == self.MI_OK):
            self.ATQA = backData[0]+(backData[1]<<8)
            buf = self.ATQA & self.ATQA_UIDMASK
            if(buf == self.ATQA_UIDSINGLE):
                self.uidLen       = 4
                self.cascadeLevel = 1
            elif (buf == self.ATQA_UIDDOUBLE):
                self.uidLen       = 7
                self.cascadeLevel = 2
            elif (buf == self.ATQA_UIDTRIPLE):
                self.uidLen       = 10
                self.cascadeLevel = 3
            if (self.DEBUG):
                print ">>UID length    = "+str(self.uidLen)
                print ">>Cascade Level = "+str(self.cascadeLevel)
        if ((status != self.MI_OK) | (backBits != 0x10)):
            status = self.MI_ERR
        return (status,backBits)
#******************************************************************************************
    def MFRC522_GetAccess(self,block):
        uid=[]
        buf=[]
        (status,TagType) = self.MFRC522_Request(self.PICC_REQIDL)                   # Scan for cards 
        if status!=self.MI_OK:
            return 0
        i=0
        while i<self.cascadeLevel:
            (status,data)=self.MFRC522_Anticoll(i)
            if status != self.MI_OK:
                if self.DEBUG:
                    print ">>Error on cascad level №"+str(i+1)
                return 0
            self.MFRC522_SelectTag(data,i)
            j=0
            while j<4:
                buf.append(data[j])
                j=j+1
            if self.DEBUG:
                print ">>Data №" + str(i+1) + " = " + str(data)
            i=i+1
        del buf[0]
        i=len(buf)
        while i>0:
            uid.append(buf[i-1])
            i=i-1
        if self.DEBUG:
            print ">>UID = " + str(uid)
        if self.tagAuth:
            i=0
            while i<len(MIFARE_CLASSIC_1K_KEYS):
                status = self.MFRC522_Auth(self.PICC_AUTHENT1A,block,MIFARE_CLASSIC_1K_KEYS[i],data)
                if status == self.MI_OK:
                    return uid
            return 0
        else:
            return uid
#******************************************************************************************

#******************************************************************************************
    def MFRC522_Anticoll(self,CLn):
        if (self.DEBUG):
            print ">>------ANTICOLL-----"
        backData    = []
        serNum      = []
        self.Write_MFRC522(self.BitFramingReg,0x00)
        serNum.append(self.PICC_ANTICOLL[CLn])
        serNum.append(0x20)
        (status,backData,backBits) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE,serNum)
        if(status == self.MI_OK)&(len(backData)==5):
            i = 0
            serNumCheck = 0
            while i<4:
                serNumCheck = serNumCheck ^ backData[i]
                i = i + 1
            if serNumCheck != backData[i]:
                status = self.MI_ERR
        return (status,backData)
#******************************************************************************************
    def CalulateCRC(self, pIndata):
        self.ClearBitMask(self.DivIrqReg, 0x04)
        self.SetBitMask(self.FIFOLevelReg, 0x80);
        i = 0
        while i<len(pIndata):
            self.Write_MFRC522(self.FIFODataReg, pIndata[i])
            i = i + 1
        self.Write_MFRC522(self.CommandReg, self.PCD_CALCCRC)
        i = 0xFF
        while True:
            n = self.Read_MFRC522(self.DivIrqReg)
            i = i - 1
            if not ((i != 0) and not (n&0x04)):
                break
        pOutData = []
        pOutData.append(self.Read_MFRC522(self.CRCResultRegL))
        pOutData.append(self.Read_MFRC522(self.CRCResultRegM))
        return pOutData
#******************************************************************************************
    def MFRC522_SelectTag(self,UID,CLn):
        if (self.DEBUG):
            print ">>------SELECT------"
        backData = []
        buf      = []
        buf.append(self.PICC_SElECTTAG[CLn])
        buf.append(0x70)
        i=0
        while i<5:
            buf.append(UID[i])
            i=i+1
        pOut = self.CalulateCRC(buf)
        buf.append(pOut[0])
        buf.append(pOut[1])
        (status,backData,backLen) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE,buf)
        if (status == self.MI_OK) & (backLen == 0x18):
            self.SAK = backData[0]
            (self.tagType,self.tagAuth) = self.mifareCardSelect(self.SAK)
            print ">>SAK         = " + str(self.SAK)
            return backData[0]
        else:
            return 0
#******************************************************************************************
    def MFRC522_Auth(self, authMode, BlockAddr, Sectorkey, serNum):
        buff = []
        # First byte should be the authMode (A or B)
        buff.append(authMode)
        # Second byte is the trailerBlock (usually 7)
        buff.append(BlockAddr)
        # Now we need to append the authKey which usually is 6 bytes of 0xFF
        i = 0
        while(i < len(Sectorkey)):
            buff.append(Sectorkey[i])
            i = i + 1
        i = 0
        # Next we append the first 4 bytes of the UID
        while(i < 4):
            buff.append(serNum[i])
            i = i +1
        # Now we start the authentication itself
        (status, backData, backLen) = self.MFRC522_ToCard(self.PCD_AUTHENT,buff)
        # Check if an error occurred
        if not(status == self.MI_OK):
            print "AUTH ERROR!!"
            return self.MI_ERR
        if not (self.Read_MFRC522(self.Status2Reg) & 0x08) != 0:
            print "AUTH ERROR(status2reg & 0x08) != 0"
            return self.MI_ERR
        # Return the status
        return status
#******************************************************************************************
    def MFRC522_StopCrypto1(self):
        self.ClearBitMask(self.Status2Reg, 0x08)
#******************************************************************************************
    def MFRC522_Read(self, blockAddr):
        recvData = []
        recvData.append(self.PICC_READ)
        recvData.append(blockAddr)
        pOut = self.CalulateCRC(recvData)
        recvData.append(pOut[0])
        recvData.append(pOut[1])
        (status, backData, backLen) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, recvData)
        if not(status == self.MI_OK):
            print "Error while reading!"
            return None
        i = 0
        if len(backData) == 16:
            print "Sector "+str(blockAddr)+" "+str(backData)
            return backData
        return None
#******************************************************************************************
    def MFRC522_Write(self, blockAddr, writeData):
        buff = []
        buff.append(self.PICC_WRITE)
        buff.append(blockAddr)
        crc = self.CalulateCRC(buff)
        buff.append(crc[0])
        buff.append(crc[1])
        (status, backData, backLen) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, buff)
        if not(status == self.MI_OK) or not(backLen == 4) or not((backData[0] & 0x0F) == 0x0A):
            status = self.MI_ERR
        #print "%s backdata &0x0F == 0x0A %s" % (backLen, backData[0]&0x0F)
        if status == self.MI_OK:
            i = 0
            buf = []
            while i < 16:
                buf.append(writeData[i])
                i = i + 1
            crc = self.CalulateCRC(buf)
            buf.append(crc[0])
            buf.append(crc[1])
            (status, backData, backLen) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE,buf)
            if not(status == self.MI_OK) or not(backLen == 4) or not((backData[0] & 0x0F) == 0x0A):
                print "Error while writing"
            if status == self.MI_OK:
                print "Data written"
#******************************************************************************************
    def MFRC522_DumpClassic1K(self, key, uid):
        i = 0
        while i < 64:
            status = self.MFRC522_Auth(self.PICC_AUTHENT1A, i, key, uid)
            # Check if authenticated
            if status == self.MI_OK:
                self.MFRC522_Read(i)
            else:
                print "Authentication error"
            i = i+1
#******************************************************************************************
    def MFRC522_Init(self):
        GPIO.output(self.NRSTPD, 1)
        self.MFRC522_Reset();
        self.Write_MFRC522(self.TModeReg,      0x8D)
        self.Write_MFRC522(self.TPrescalerReg, 0x3E)
        self.Write_MFRC522(self.TReloadRegL,     30)
        self.Write_MFRC522(self.TReloadRegH,      0)
        self.Write_MFRC522(self.TxASKReg,      0x40)
        self.Write_MFRC522(self.ModeReg,       0x3D)
        self.AntennaOn()
#******************************************************************************************
#******************************************************************************************
#******************************************************************************************