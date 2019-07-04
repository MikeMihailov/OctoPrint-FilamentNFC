# OctoPrint-Filamentnfc

Octoprint plugin that scan nfc tag on the spool via RC522. You can storage the information about the filament, that:

1. Material type    
2. Color    
3. Weight    
4. Current weight balance    
5. Diametr of filament    
6. Price    
7. Vender name    
8. Plastic density    
9. Extruder minimum temperature    
10. Extruder maximum temperature    
11. Hotbed minimum temperature    
12. Hotbed maximum temperature    

In common mode plugin try to scan tag every 3 seconds (You can change this interval in settings). When tag is found, plugin will read data from tag. After that you can see filament data on the siderbar and in settings. Data will be frozen for next reading.    
![Side bar](/Screenshot/FirstScreen.png)
Plugn support Mifare Classic 1K and Mifare Ultralight tags.    
You can write filament data into nfc tag in settigs:
![Settings](/Screenshot/SettingsScreen.png)

## Mounting

If spool holder locate on the priner side (like Ultimaker), you can drill holls and mount RC522 on it. There is drill layout for RC522 in "drillLayout" directory. Just print picture and use drill Ø3 mm. Use column to setup gap between RC522 and spool.

![Drill layout](/drillLayout/DrillLayout.png)

## Wiring

Connect RC522-Raspberry Pi:    
SDA  -> pin 24    
SCK  -> pin 23    
MOSI -> pin 19    
MISO -> pin 21    
RQ   -> UNUSED    
GND  -> pin 6    
RST  -> pin 22    
3.3V -> pin 1    

## Setup

1. Init SPI:    
    sudo raspi-config:
    Inteface option -> SPI -> <Yes>
2. Install library via SSH:
    $ source ~/oprint/bin/activate    
    $ pip install RPi.GPIO    
    $ pip install spidev    
3. Install plugin:
    Install manually using this URL:
    https://github.com/photo-mickey/OctoPrint-Filamentnfc/archive/master.zip

## Configuration

1. If you cant see the FilamentNFC tab on the sidebar, please open the log and go to 'Setup' section of Readme    
2. If you see in the FilamentNFC tab "Status: RC522 communication ERROR!", please check connection in 'Wiring' section of Readme    
3. If you see in the FilamentNFC tab "Status: Online" - go next    
2. Put the nfc tag on your spool and install it in to the printer    
3. Go FilamentNFC settings    
4. Change your local currency simbol (just copy/paste)    
5. Turn the spool so that you combine the tag is facing the RC522 ("Tag: No tag" turn into "Tag detected")    
6. Press "Stop scanning"    
7. Put filament data in to the filds    
8. Press "Write"    
9. Press "Start scanning"    


## Used extra libraries: 

https://github.com/mxgxw/MFRC522-python.git    
https://github.com/niccokunzmann/crc8    
