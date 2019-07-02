# OctoPrint-Filamentnfc

## Use: 

https://github.com/mxgxw/MFRC522-python.git
https://github.com/niccokunzmann/crc8

## Wiring

Connect RDID-RC522:

SDA  -> pin 24
SCK  -> pin 23
MOSI -> pin 19
MISO -> pin 21
RQ   -> no
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

