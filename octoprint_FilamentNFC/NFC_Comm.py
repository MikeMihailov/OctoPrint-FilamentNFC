# TODO:
# 2. Material density
# 2. Memory map correction
# 3. CRC control
# 4. beckup memory region
# 5. try to read from beckup, if CRC fail
# 6. On/Off debug mode
# 7. gr2mm, mm2gr, gr2mony functions
# 8. balance in % function
# 9. color in HEX ????
#*******************************************************************************
#***************************INCLIDE*********************************************
#*******************************************************************************
from PlasticData import spool,material,colorStr
import MFRC522
import RPi.GPIO as GPIO
import signal
import time
import binascii
#*******************************************************************************
#**************************CONSTANT*********************************************
#*******************************************************************************
keyA = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
#*******************************************************************************
#*************************MEMORY MAP********************************************
#*******************************************************************************
#   |-15-14-13-|-12-11-|--10--9--|--8-|-7--|---6-|5---|---4-|--3----2--|---1--0---|
# 4 | RESERVED | price | diametr | balance |   weight |      color     | material |
# 5 |                           V E N D O R     N A M E                           |
# 6 |         R E S E R V E D         |bedMaxTemp|bedMinTemp|extMaxTemp|extMinTemp|
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
        blockNumber   = 4		# because gladiolus
        tag   = MFRC522.MFRC522()
        spool = spool()
        
        # Ready!
        def checkTag(self, block):
                (status,TagType) = self.tag.MFRC522_Request(self.tag.PICC_REQIDL)							# Scan for cards 
                if status == self.tag.MI_OK:															    # If a card is found
                        (status,uid) = self.tag.MFRC522_Anticoll()								            # Get the UID of the card
                        if status == self.tag.MI_OK:							                            # If we have the UID, continue
                                self.tag.MFRC522_SelectTag(uid)												# Select the scanned tag
                                status = self.tag.MFRC522_Auth(self.tag.PICC_AUTHENT1A, block, keyA, uid)	# Authenticate
                                if status == self.tag.MI_OK:												# Check if authenticated
                                        return 1
                return 0
        # Ready!
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
        # Ready!
        def readAll(self):
                data = []
                for x in range(0,64):
                    stat = 0
                    while (stat == 0):
                            stat = self.checkTag(x)
                    data = self.readData(x)
                    print "Sector "+str(x)+" "+str(data)
                        
        def readSpool(self):
                data = []
                #***********BLOCK 4***********
                stat = 0
                while (stat == 0):
                    stat = self.checkTag(self.blockNumber)
                data = self.readData(self.blockNumber)
                if len(data) == 16:
                        self.spool.material = data[materialAdr] | data[materialAdr+1]<<8
                        self.spool.color    = data[colorAdr]    | data[colorAdr+1]<<8
                        self.spool.weight   = data[weightAdr]   | data[weightAdr+1]<<8
                        self.spool.balance  = data[balanceAdr]  | data[balanceAdr+1]<<8
                        self.spool.diametr  = data[diametrAdr]  | data[diametrAdr+1]<<8
                        self.spool.price    = data[priceAdr]    | data[priceAdr+1]<<8
                        self.spool.density  = data[densityAdr]  | data[densityAdr+1]<<8
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
                else:
                        return 0
                #********DEBUG******
                print "********READING********"
                print "material   = " + material[self.spool.material]
                print "color      = " + colorStr[self.spool.color]
                print "weight     = " + str(self.spool.weight) + " gr"
                print "balance    = " + str(self.spool.balance) + " gr"
                print "diametr    = " + str(self.spool.diametr*0.01) + " mm"
                print "price      = " + str(self.spool.price) + " rub"
                print "vender     = " + str(self.spool.vender) + " mm"
                print "density    = " + str(self.spool.density*0.01)
                print "extMinTemp = " + str(self.spool.extMinTemp) + " 'C"
                print "extMaxTemp = " + str(self.spool.extMaxTemp) + " 'C"
                print "bedMinTemp = " + str(self.spool.bedMinTemp) + " 'C"
                print "bedMaxTemp = " + str(self.spool.bedMaxTemp) + " 'C"
                print "***********************"
                #*******************
                return 1

        def writeSpool(self):
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
                
                outData[densityAdr]    = self.spool.density         & 0xFF
                outData[densityAdr+1]  = (self.spool.density>>8)    & 0xFF
                
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
                while (stat == 0):
                    stat = self.checkTag(self.blockNumber+2)
                self.tag.MFRC522_Write(self.blockNumber+2, outData)	# Write the data
                self.tag.MFRC522_StopCrypto1()
                
                print "DONE"
                return 0
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
                NFC.readSpool()
                print "*******************************************"
                #data = NFC.readSpool()
                #if (data != 0):
                #    print "Sector "+str(NFC.dataBlock)+" "+str(data)
                #    print "*******************************************"
                #    stat = 0
                #    while (stat == 0):
                #        stat = NFC.writeSpool()
                #print "*******************************************"
                time.sleep(10)
#*******************************************************************************
#*******************************************************************************
#*******************************************************************************