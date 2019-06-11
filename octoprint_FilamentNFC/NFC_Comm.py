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
#*************************MEMORY MAP********************************************
#*******************************************************************************
#   |--15----14--|--13----12--|-11---10-|-9-----8-|--7----6--|--5----4--|--3----2--|--1----0--|
# 4 |  RESERVED  |   density  |  price  | diametr |  balance |  weight  |   color  | material |
# 5 |                                 V E N D O R     N A M E                                 |
# 6 | CRC8 |       R E S E R V E D                |bedMaxTemp|bedMinTemp|extMaxTemp|extMinTemp|
#*******************************************************************************
# block 4
materialAdr   = 0	# 2 bytes
colorAdr      = 2	# 2 bytes
weightAdr     = 4	# 2 bytes
balanceAdr    = 6	# 2 bytes
diametrAdr    = 8   # 2 bytes
priceAdr	  = 10	# 2 bytes
densityAdr    = 12  # 2 bytes
# block 5
venderAdr     = 0	# 16 bytes
# block 6
extMinTempAdr = 0   # 2 bytes
extMaxTempAdr = 2   # 2 bytes
bedMinTempAdr = 4   # 2 bytes
bedMaxTempAdr = 6   # 2 bytes
heshAdr       = 15  # 1 byte
# sum 29 bytes = 2 blocks
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
class NFC:
        blockNumber   = 4		    # because gladiolus
        DEBUG         = 1           # On/Off debug print
        tag           = MFRC522()
        spool         = spool()
        hashCalc      = crc()
        hashRead      = 0
        validData     = 0

        def checkTag(self, block):
                (status,TagType) = self.tag.MFRC522_Request(self.tag.PICC_REQIDL)							# Scan for cards 
                if status == self.tag.MI_OK:															    # If a card is found
                        (status,uid) = self.tag.MFRC522_Anticoll()								            # Get the UID of the card
                        if status == self.tag.MI_OK:							                            # If we have the UID, continue
                                self.tag.MFRC522_SelectTag(uid)												# Select the scanned tag
                                status = self.tag.MFRC522_Auth(self.tag.PICC_AUTHENT1A, block, keyA, uid)	# Authenticate
                                if status == self.tag.MI_OK:												# Check if authenticated
                                        return uid
                return 0

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

        def readAll(self):
                data = []
                for x in range(0,64):
                    stat = 0
                    while (stat == 0):
                            stat = self.checkTag(x)
                    data = self.readData(x)
                    print "Sector "+str(x)+" "+str(data)
                      
        def gr2mm(self,gr):
                return gr/(self.spool.density * (math.pi*(self.spool.diametr/2)**2) * 0,001)
        
        def mm2gr(self,mm):
                return self.spool.density * (math.pi*(self.spool.diametr/2)**2) * mm * 0,001
                
        def gr2mony(self,gr):
                return gr*self.spool.price/self.spool.weight
        
        def mm2mony(self,mm):
                gr = self.mm2gr(mm)
                return self.gr2mony(gr)
                
        def balancePercent(self):
                return self.spool.balance*100/self.spool.weight
        
        def readSpool(self):
                data = []
                self.hashCalc.__init__()
                #***********BLOCK 4***********
                stat = 0
                while (stat == 0):
                    stat = self.checkTag(self.blockNumber)
                self.spool.uid =  stat[0] | stat[1] << 8 | stat[2] << 16 | stat[3] << 24 | stat[4] << 32
                data = self.readData(self.blockNumber)
                if len(data) == 16:
                        self.spool.material = data[materialAdr] | data[materialAdr+1]<<8
                        self.spool.color    = data[colorAdr]    | data[colorAdr+1]<<8
                        self.spool.weight   = data[weightAdr]   | data[weightAdr+1]<<8
                        self.spool.balance  = data[balanceAdr]  | data[balanceAdr+1]<<8
                        self.spool.diametr  = data[diametrAdr]  | data[diametrAdr+1]<<8
                        self.spool.price    = data[priceAdr]    | data[priceAdr+1]<<8
                        self.spool.density  = data[densityAdr]  | data[densityAdr+1]<<8
                        for i in range(0,16):
                                self.hashCalc.update(chr(data[i]))
                else: 
                        return 0
                #***********BLOCK 5***********
                stat = 0
                while (stat == 0):
                    stat = self.checkTag(self.blockNumber+1)
                data = self.readData(self.blockNumber+1)
                if len(data) == 16:
                        self.spool.vender = ''
                        for i in range(0,16):
                                self.spool.vender += chr(data[i])
                                self.hashCalc.update(chr(data[i]))
                else:
                        return 0
                #***********BLOCK 6***********
                stat = 0
                while (stat == 0):
                    stat = self.checkTag(self.blockNumber+2)
                data = self.readData(self.blockNumber+2)
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
                        print "diametr    = " + str(self.spool.diametr*0.01) + " mm"
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

        def writeSpool(self):
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
                
                outData[diametrAdr]    = self.spool.diametr       & 0xFF
                outData[diametrAdr+1]  = (self.spool.diametr>>8)  & 0xFF
                
                outData[priceAdr]      = self.spool.price         & 0xFF
                outData[priceAdr+1]    = (self.spool.price>>8)    & 0xFF
                
                outData[densityAdr]    = self.spool.density       & 0xFF
                outData[densityAdr+1]  = (self.spool.density>>8)  & 0xFF
                
                for i in range (0,16):
                    self.hashCalc.update(chr(outData[i]))   
                
                while (stat == 0):
                        stat = self.checkTag(self.blockNumber)
                self.tag.MFRC522_Write(self.blockNumber, outData)	# Write the data
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
                        stat = self.checkTag(self.blockNumber+1)
                self.tag.MFRC522_Write(self.blockNumber+1, outData)	# Write the data
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
                        stat = self.checkTag(self.blockNumber+2)
                
                self.tag.MFRC522_Write(self.blockNumber+2, outData)	# Write the data
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
        NFC = NFC()
        print "*******************************************"
        print "NFC test:"
        print "*******************************************"
        while(continue_reading):
                #NFC.readAll()
                #NFC.writeSpool()
                print "*******************************************"
                time.sleep(1)
                NFC.readSpool()
                print "*******************************************"
                time.sleep(10)
#*******************************************************************************
#*******************************************************************************
#*******************************************************************************
