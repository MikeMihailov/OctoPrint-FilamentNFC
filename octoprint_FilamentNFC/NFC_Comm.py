# TODO:
# 4. beckup memory region
# 5. try to read from beckup, if CRC fail
# 9. color in HEX ????
# 10. error control (color and material out of range
# DONE:
# 1. Material density
# 2. Memory map correction
# 3. CRC control
# 7. gr2mm, mm2gr, gr2mony functions
# 8. balance in % function
# 6. On/Off debug mode
#*******************************************************************************
#***************************INCLIDE*********************************************
#*******************************************************************************
from PlasticData import spool,material,colorStr
from MFRC522 import MFRC522
import RPi.GPIO as GPIO
import signal
import time
import binascii
import math
from crc8 import crc
#*******************************************************************************
#**************************CONSTANT*********************************************
#*******************************************************************************
keyA = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
#*******************************************************************************
#********************MEMORY MAP MIFARE CLASSIC**********************************
#*******************************************************************************
#   |--15----14--|--13----12--|-11---10-|-9-----8-|--7----6--|--5----4--|--3----2--|--1----0--|
# 4 |  RESERVED  |   density  |  price  | diameter |  balance |  weight  |   color  | material |
# 5 |                                 V E N D O R     N A M E                                 |
# 6 | CRC8 |       R E S E R V E D                |bedMaxTemp|bedMinTemp|extMaxTemp|extMinTemp|
#*******************************************************************************
# block 4
materialAdr   = 0   # 2 bytes
colorAdr      = 2   # 2 bytes
weightAdr     = 4   # 2 bytes
balanceAdr    = 6   # 2 bytes
diameterAdr   = 8   # 2 bytes
priceAdr      = 10  # 2 bytes
densityAdr    = 12  # 2 bytes
# block 5
venderAdr     = 0   # 16 bytes
# block 6
extMinTempAdr = 0   # 2 bytes
extMaxTempAdr = 2   # 2 bytes
bedMinTempAdr = 4   # 2 bytes
bedMaxTempAdr = 6   # 2 bytes
heshAdr       = 15  # 1 byte
# sum 29 bytes = 2 blocks
#*******************************************************************************
#******************MEMORY MAP MIFARE ULTRALIGHT*********************************
#*******************************************************************************
#    |--3----2--|--1----0--|
#  4 |   color  | material |
#  5 |  balance |  weight  |
#  6 |  price   | diameter  |
#  7 | RESERVED |  density |
#  8 |    VENDOR NAME 0    |
#  9 |    VENDOR NAME 1    |
# 10 |    VENDOR NAME 2    |
# 11 |    VENDOR NAME 3    |
# 12 |extMaxTemp|extMinTemp|
# 13 |bedMaxTemp|bedMinTemp|
# 14 |      RESERVED       |
# 15 | CRC8 |   RESERVED   |
#*******************************************************************************
#*****************************VAR***********************************************
#*******************************************************************************
continue_reading = True
#*******************************************************************************
#*******************************************************************************
#*******************************************************************************
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    self.continue_reading = False
    GPIO.cleanup()
#*******************************************************************************
#*******************************************************************************
#*******************************************************************************
class NFCmodule:
    def __init__(self):
        self.spool         = spool()
        #self.spool.clean()
        self.tag           = MFRC522()
        self.hashCalc      = crc()
        self.validData     = 0
        self.hashRead      = 0
        self.blockNumber   = 4           # because gladiolus
        self.DEBUG         = 1           # On/Off debug print
        self.scanAttempts  = 2
#******************************************************************************************
    def readData(self,block):
        recvData = []
        recvData.append(self.tag.PICC_READ)
        recvData.append(block)
        pOut = self.tag.CalulateCRC(recvData)
        recvData.append(pOut[0])
        recvData.append(pOut[1])
        (status, backData, backLen) = self.tag.MFRC522_ToCard(self.tag.PCD_TRANSCEIVE, recvData)
        self.tag.MFRC522_StopCrypto1()
        if status == self.tag.MI_OK:
            return backData
        return 0
#******************************************************************************************
    def readAll(self):
        data = []
        stat = 0
        if (self.tag.tagType == self.tag.mifareUltralight):
            while (stat == 0):
                stat = self.tag.MFRC522_GetAccess(0)
                memSize = self.tag.memSize
        else:
            memSize=1
        x=0
        while x<memSize:
            if (self.tag.tagType != self.tag.mifareUltralight):
                stat = 0
                while (stat == 0):
                    stat = self.tag.MFRC522_GetAccess(x)
                    memSize = self.tag.memSize
            data = self.tag.MFRC522_Read(x)
            if (self.tag.tagType != self.tag.mifareUltralight):
                self.tag.MFRC522_StopCrypto1()
            else:
                i=0
                while i<12:
                    del data[15-i]
                    i=i+1
            print "Sector "+str(x)+" "+str(data)
            x=x+1
        self.tag.MFRC522_StopCrypto1()
        return 1
#******************************************************************************************
    def gr2mm(self,gr):
        return gr/(self.spool.density * (math.pi*(self.spool.diameter/2)**2) * 0,001)
#******************************************************************************************
    def mm2gr(self,mm):
        return self.spool.density * (math.pi*(self.spool.diameter/2)**2) * mm * 0,001
#******************************************************************************************
    def gr2mony(self,gr):
        return gr*self.spool.price/self.spool.weight
#******************************************************************************************
    def mm2mony(self,mm):
        gr = self.mm2gr(mm)
        return self.gr2mony(gr)
#******************************************************************************************
    def balancePercent(self):
        return self.spool.balance*100/self.spool.weight
#******************************************************************************************
    def getUidStr(self,uid):
        i=0
        out=0
        while i<self.tag.uidLen:
            out=out|(uid[i]<<(8*i))
            i=i+1
        return out
#******************************************************************************************
    def readSpool(self):
        uid = 0
        for att in range(self.scanAttempts):
            uid = self.tag.MFRC522_GetAccess(self.blockNumber)
            if uid != 0:
                break
        if uid == 0:
            return 0
        self.spool.uid = self.getUidStr(uid)
        if (self.tag.tagType != self.tag.mifareUltralight):
            self.readSpoolClassic()
        else:
            self.readSpoolUtl()
        return 1
#******************************************************************************************
    def readSpoolUtl(self):
        data = []
        self.hashCalc.__init__()
        curBlock = self.blockNumber
        #***********BLOCK 4***********
        data = self.tag.MFRC522_Read(curBlock)
        if len(data) == 16:
            self.spool.material = data[0] | data[1]<<8
            self.spool.color    = data[2] | data[3]<<8
            i=0
            while i<4:
                self.hashCalc.update(chr(data[i]))
                i=i+1
            curBlock=curBlock+1
        else:
            return 0
        #***********BLOCK 5***********
        data = self.tag.MFRC522_Read(curBlock)
        if len(data) == 16:
            self.spool.weight   = data[0] | data[1]<<8
            self.spool.balance  = data[2] | data[3]<<8
            i=0
            while i<4:
                self.hashCalc.update(chr(data[i]))
                i=i+1
            curBlock=curBlock+1
        else:
            return 0
        #***********BLOCK 6***********
        data = self.tag.MFRC522_Read(curBlock)
        if len(data) == 16:
            self.spool.diameter  = data[0] | data[1]<<8
            self.spool.price    = data[2] | data[3]<<8
            i=0
            while i<4:
                self.hashCalc.update(chr(data[i]))
                i=i+1
            curBlock=curBlock+1
        else:
            return 0
        #***********BLOCK 7***********
        data = self.tag.MFRC522_Read(curBlock)
        if len(data) == 16:
            self.spool.density   = data[0] | data[1]<<8
            while i<4:
                self.hashCalc.update(chr(data[i]))
                i=i+1
            curBlock=curBlock+1
        else:
            return 0
        #***********BLOCK 8,9,10,11***********
        self.spool.vender = ''
        j=0
        while j<4:
            data = self.tag.MFRC522_Read(curBlock)
            if len(data) == 16:
                i=0
                while i<4:
                    self.spool.vender += chr(data[i])
                    self.hashCalc.update(chr(data[i]))
                    i=i+1
                curBlock=curBlock+1
            else:
                return 0
            j=j+1
        #***********BLOCK 12**********
        data = self.tag.MFRC522_Read(curBlock)
        if len(data) == 16:
            self.spool.extMinTemp = data[0] | data[1]<<8
            self.spool.extMaxTemp = data[2] | data[3]<<8
            i=0
            while i<4:
                self.hashCalc.update(chr(data[i]))
                i=i+1
            curBlock=curBlock+1
        else:
            return 0
        #***********BLOCK 13**********
        data = self.tag.MFRC522_Read(curBlock)
        if len(data) == 16:
            self.spool.bedMinTemp = data[0] | data[1]<<8
            self.spool.bedMaxTemp = data[2] | data[3]<<8
            i=0
            while i<4:
                self.hashCalc.update(chr(data[i]))
                i=i+1
            curBlock=curBlock+1
        else:
            return 0
        #***********BLOCK 14**********
        data = self.tag.MFRC522_Read(curBlock)
        if len(data) == 16:
            i=0
            while i<4:
                self.hashCalc.update(chr(data[i]))
                i=i+1
            curBlock=curBlock+1
        else:
            return 0
        #***********BLOCK 15**********
        data = self.tag.MFRC522_Read(curBlock)
        self.tag.MFRC522_StopCrypto1()
        if len(data) == 16:
            self.hashRead         = data[3]
            i=0
            while i<3:
                self.hashCalc.update(chr(data[i]))
                i=i+1
            curBlock=curBlock+1
        else:
            return 0
        if int(self.hashCalc.hexdigest(),16) == self.hashRead:
            validData = 1
        else:
            validData = 0
            #return 0
        if (self.DEBUG == 1):
            print "uid        = " + str(hex(self.spool.uid))
            print "material   = " + material[self.spool.material]
            print "color      = " + colorStr[self.spool.color]
            print "weight     = " + str(self.spool.weight) + " gr"
            print "balance    = " + str(self.spool.balance) + " gr"
            print "diameter    = " + str(self.spool.diameter*0.01) + " mm"
            print "price      = " + str(self.spool.price) + " rub"
            print "vender     = " + str(self.spool.vender)
            print "density    = " + str(self.spool.density*0.01) + " gr/cm^3"
            print "extMinTemp = " + str(self.spool.extMinTemp) + " 'C"
            print "extMaxTemp = " + str(self.spool.extMaxTemp) + " 'C"
            print "bedMinTemp = " + str(self.spool.bedMinTemp) + " 'C"
            print "bedMaxTemp = " + str(self.spool.bedMaxTemp) + " 'C"
            print "hash calc  = " + str(hex(int(self.hashCalc.hexdigest(),16)))
            print "hash read  = " + str(hex(self.hashRead))
            print "hash valid = " + str(validData)
#******************************************************************************************
    def readSpoolClassic(self):
        data = []
        self.hashCalc.__init__()
        #***********BLOCK 4***********
        data = self.tag.MFRC522_Read(self.blockNumber)
        self.tag.MFRC522_StopCrypto1()
        if len(data) == 16:
            self.spool.material = data[materialAdr] | data[materialAdr+1]<<8
            self.spool.color    = data[colorAdr]    | data[colorAdr+1]<<8
            self.spool.weight   = data[weightAdr]   | data[weightAdr+1]<<8
            self.spool.balance  = data[balanceAdr]  | data[balanceAdr+1]<<8
            self.spool.diameter  = data[diameterAdr]  | data[diameterAdr+1]<<8
            self.spool.price    = data[priceAdr]    | data[priceAdr+1]<<8
            self.spool.density  = data[densityAdr]  | data[densityAdr+1]<<8
            for i in range(0,16):
                self.hashCalc.update(chr(data[i]))
        else:
            return 0
        #***********BLOCK 5***********
        stat = 0
        for att in range(self.scanAttempts):
            stat = self.tag.MFRC522_GetAccess(self.blockNumber+1)
            if stat != 0:
                break
        if stat == 0:
            return 0
        data = self.tag.MFRC522_Read(self.blockNumber+1)
        self.tag.MFRC522_StopCrypto1()
        if len(data) == 16:
            self.spool.vender = ''
            for i in range(0,16):
                self.spool.vender += chr(data[i])
                self.hashCalc.update(chr(data[i]))
        else:
            return 0
        #***********BLOCK 6***********
        stat = 0
        for att in range(self.scanAttempts):
            stat = self.tag.MFRC522_GetAccess(self.blockNumber+2)
            if stat != 0:
                break
        if stat == 0:
            return 0
        data = self.tag.MFRC522_Read(self.blockNumber+2)
        self.tag.MFRC522_StopCrypto1()
        if len(data) == 16:
            self.spool.extMinTemp = data[extMinTempAdr] | data[extMinTempAdr+1]<<8
            self.spool.extMaxTemp = data[extMaxTempAdr] | data[extMaxTempAdr+1]<<8
            self.spool.bedMinTemp = data[bedMinTempAdr] | data[bedMinTempAdr+1]<<8
            self.spool.bedMaxTemp = data[bedMaxTempAdr] | data[bedMaxTempAdr+1]<<8
            self.hashRead         = data[heshAdr]
            for i in range(0,15):
                self.hashCalc.update(chr(data[i]))
        else:
            return 0
        if int(self.hashCalc.hexdigest(),16) == self.hashRead:
            validData = 1
        else:
            validData = 0
            return 0
        #********DEBUG******
        if (self.DEBUG == 1):
            print "uid        = " + str(hex(self.spool.uid))
            print "material   = " + material[self.spool.material]
            print "color      = " + colorStr[self.spool.color]
            print "weight     = " + str(self.spool.weight) + " gr"
            print "balance    = " + str(self.spool.balance) + " gr"
            print "diameter    = " + str(self.spool.diameter*0.01) + " mm"
            print "price      = " + str(self.spool.price) + " rub"
            print "vender     = " + str(self.spool.vender)
            print "density    = " + str(self.spool.density*0.01) + " gr/cm^3"
            print "extMinTemp = " + str(self.spool.extMinTemp) + " 'C"
            print "extMaxTemp = " + str(self.spool.extMaxTemp) + " 'C"
            print "bedMinTemp = " + str(self.spool.bedMinTemp) + " 'C"
            print "bedMaxTemp = " + str(self.spool.bedMaxTemp) + " 'C"
            print "hash calc  = " + str(hex(int(self.hashCalc.hexdigest(),16)))
            print "hash read  = " + str(hex(self.hashRead))
            print "hash valid = " + str(validData)
        #*******************
        return 1
#******************************************************************************************
    def writeSpool(self):
        uid = 0
        for att in range(self.scanAttempts):
            uid = self.tag.MFRC522_GetAccess(self.blockNumber)
            if uid != 0:
                break
        if uid == 0:
            return 0
        self.spool.uid = self.getUidStr(uid)
        if (self.tag.tagType != self.tag.mifareUltralight):
            self.writeSpoolClassic()
        else:
            self.writeSpoolUtl()
        return
#******************************************************************************************
    def writeSpoolUtl(self):
        self.hashCalc.__init__()
        outData = []
        for i in range(0,16):
            outData.append(0x00)
        curBlock = self.blockNumber
        #***********BLOCK 4***********
        outData[0] = self.spool.material      & 0xFF
        outData[1] = (self.spool.material>>8) & 0xFF
        outData[2] = self.spool.color         & 0xFF
        outData[3] = (self.spool.color>>8)    & 0xFF
        for i in range (0,4):
            self.hashCalc.update(chr(outData[i]))
        self.tag.MFRC522_Write(curBlock,outData)   # Write the data
        curBlock=curBlock+1
        #***********BLOCK 5***********
        outData = []
        for i in range(0,16):
            outData.append(0x00)
        outData[0] = self.spool.weight       & 0xFF
        outData[1] = (self.spool.weight>>8)  & 0xFF
        outData[2] = self.spool.balance      & 0xFF
        outData[3] = (self.spool.balance>>8) & 0xFF
        for i in range (0,4):
            self.hashCalc.update(chr(outData[i]))
        self.tag.MFRC522_Write(curBlock,outData)   # Write the data
        curBlock=curBlock+1
        #***********BLOCK 6***********
        outData = []
        for i in range(0,16):
            outData.append(0x00)
        outData[0] = self.spool.diameter      & 0xFF
        outData[1] = (self.spool.diameter>>8) & 0xFF
        outData[2] = self.spool.price        & 0xFF
        outData[3] = (self.spool.price>>8)   & 0xFF
        for i in range (0,4):
            self.hashCalc.update(chr(outData[i]))
        self.tag.MFRC522_Write(curBlock,outData)   # Write the data
        curBlock=curBlock+1
        #***********BLOCK 7***********
        outData = []
        for i in range(0,16):
            outData.append(0x00)
        outData[0] = self.spool.density      & 0xFF
        outData[1] = (self.spool.density>>8) & 0xFF
        for i in range (0,4):
            self.hashCalc.update(chr(outData[i]))
        self.tag.MFRC522_Write(curBlock,outData)   # Write the data
        curBlock=curBlock+1
        #***********BLOCK 8,9,10,11***********
        z = 0
        strLen = len(self.spool.vender)
        for j in range (0,4):
            outData = []
            for i in range(0,16):
                outData.append(0x00)
            for i in range(0,4):
                if z<strLen:
                    outData[i] = ord(self.spool.vender[z])
                else:
                    outData[i] = ord(' ')
                z=z+1
                self.hashCalc.update(chr(outData[i]))
            self.tag.MFRC522_Write(curBlock,outData)   # Write the data
            curBlock=curBlock+1
        #***********BLOCK 12**********
        outData = []
        for i in range(0,16):
            outData.append(0x00)
        outData[0] = self.spool.extMinTemp      & 0xFF
        outData[1] = (self.spool.extMinTemp>>8) & 0xFF
        outData[2] = self.spool.extMaxTemp      & 0xFF
        outData[3] = (self.spool.extMaxTemp>>8) & 0xFF
        for i in range (0,4):
            self.hashCalc.update(chr(outData[i]))
        self.tag.MFRC522_Write(curBlock,outData)   # Write the data
        curBlock=curBlock+1
        #***********BLOCK 13**********
        outData = []
        for i in range(0,16):
            outData.append(0x00)
        outData[0] = self.spool.bedMinTemp      & 0xFF
        outData[1] = (self.spool.bedMinTemp>>8) & 0xFF
        outData[2] = self.spool.bedMaxTemp      & 0xFF
        outData[3] = (self.spool.bedMaxTemp>>8) & 0xFF
        for i in range (0,4):
            self.hashCalc.update(chr(outData[i]))
        self.tag.MFRC522_Write(curBlock,outData)   # Write the data
        curBlock=curBlock+1
        #***********BLOCK 14**********
        outData = []
        for i in range(0,16):
            outData.append(0x00)
        #RESERVED
        for i in range (0,4):
            self.hashCalc.update(chr(outData[i]))
        self.tag.MFRC522_Write(curBlock,outData)   # Write the data
        curBlock=curBlock+1
        #***********BLOCK 15**********
        outData = []
        for i in range(0,16):
            outData.append(0x00)
        #RESERVED
        for i in range (0,3):
            self.hashCalc.update(chr(outData[i]))
        outData[3] = int(self.hashCalc.hexdigest(),16)
        self.hashCalc.__init__()
        self.tag.MFRC522_Write(curBlock,outData)   # Write the data
        
        print "DONE!"

#******************************************************************************************
    def writeSpoolClassic(self):
        self.hashCalc.__init__()
        outData = []
        for i in range(0,16):
            outData.append(0x00)
        #***********BLOCK 4***********
        stat = 0
        outData[materialAdr]   = self.spool.material      & 0xFF
        outData[materialAdr+1] = (self.spool.material>>8) & 0xFF
        outData[colorAdr]      = self.spool.color         & 0xFF
        outData[colorAdr+1]    = (self.spool.color>>8)    & 0xFF
        outData[weightAdr]     = self.spool.weight        & 0xFF
        outData[weightAdr+1]   = (self.spool.weight>>8)   & 0xFF
        outData[balanceAdr]    = self.spool.balance       & 0xFF
        outData[balanceAdr+1]  = (self.spool.balance>>8)  & 0xFF
        outData[diameterAdr]    = self.spool.diameter       & 0xFF
        outData[diameterAdr+1]  = (self.spool.diameter>>8)  & 0xFF
        outData[priceAdr]      = self.spool.price         & 0xFF
        outData[priceAdr+1]    = (self.spool.price>>8)    & 0xFF
        outData[densityAdr]    = self.spool.density       & 0xFF
        outData[densityAdr+1]  = (self.spool.density>>8)  & 0xFF
        for i in range (0,16):
            self.hashCalc.update(chr(outData[i]))
        #while (stat == 0):
        #    stat = self.tag.MFRC522_GetAccess(self.blockNumber)
        self.tag.MFRC522_Write(self.blockNumber, outData)   # Write the data
        self.tag.MFRC522_StopCrypto1()
        #***********BLOCK 5***********
        stat = 0
        outData = []
        for i in range(0,16):
            outData.append(0x00)
        l = len(self.spool.vender)
        if (l > 16):
            l = 16
        for i in range(0,l):
            outData[i] = ord(self.spool.vender[i])
        for i in range(0,16):
            self.hashCalc.update(chr(outData[i])) 
        while (stat == 0):
            stat = self.tag.MFRC522_GetAccess(self.blockNumber+1)
        self.tag.MFRC522_Write(self.blockNumber+1, outData) # Write the data
        self.tag.MFRC522_StopCrypto1()
        #***********BLOCK 6***********
        stat = 0
        outData = []
        for i in range(0,16):
            outData.append(0x00)
        outData[extMinTempAdr]   = self.spool.extMinTemp      & 0xFF
        outData[extMinTempAdr+1] = (self.spool.extMinTemp>>8) & 0xFF
        outData[extMaxTempAdr]   = self.spool.extMaxTemp      & 0xFF
        outData[extMaxTempAdr+1] = (self.spool.extMaxTemp>>8) & 0xFF
        outData[bedMinTempAdr]   = self.spool.bedMinTemp      & 0xFF
        outData[bedMinTempAdr+1] = (self.spool.bedMinTemp>>8) & 0xFF
        outData[bedMaxTempAdr]   = self.spool.bedMaxTemp      & 0xFF
        outData[bedMaxTempAdr+1] = (self.spool.bedMaxTemp>>8) & 0xFF
        for i in range (0,15):
            self.hashCalc.update(chr(outData[i]))   
        outData[heshAdr] = int(self.hashCalc.hexdigest(),16)
        self.hashCalc.__init__()
        while (stat == 0):
            stat = self.tag.MFRC522_GetAccess(self.blockNumber+2)
        self.tag.MFRC522_Write(self.blockNumber+2, outData) # Write the data
        self.tag.MFRC522_StopCrypto1()
        if (self.DEBUG == 1):
            print "DONE"
        return 1
#*******************************************************************************
#*******************************************************************************
#*******************************************************************************
if __name__ == "__main__":
    GPIO.setwarnings(False)
    signal.signal(signal.SIGINT, end_read)  # Hook the SIGINT
    GPIO.cleanup()
    NFC = NFCmodule()
    print "*******************************************"
    print "NFC test:"
    print "*******************************************"
    while(continue_reading):
        #NFC.readAll()
        NFC.writeSpool()
        print "*******************************************"
        time.sleep(1)
        NFC.readSpool()
        print "*******************************************"
        time.sleep(10)
#*******************************************************************************
#*******************************************************************************
#*******************************************************************************
