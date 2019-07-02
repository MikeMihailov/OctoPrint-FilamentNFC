# OctoPrint-Filamentnfc

## Use: 

https://github.com/mxgxw/MFRC522-python.git    
https://github.com/niccokunzmann/crc8    

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
    Inteface option -> SPI ->  Yes    
2. Install library:    
    source ~/oprint/bin/activate    
    pip install RPi.GPIO    
    pip install spidev    
3. Install plugin:    
    Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
    or manually using this URL:
    https://github.com/photo-mickey/OctoPrint-Filamentnfc/archive/master.zip

## Configuration

1. If you cant see the FilamentNFC tab on the sidebar, please open the log and 'Setup' section of Readme    
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
