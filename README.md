# OctoPrint-Filamentnfc

## Use: 

https://github.com/mxgxw/MFRC522-python.git
https://github.com/lthiery/SPI-Py.git
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
	sudo raspi-config
	Inteface option -> SPI ->  <Yes>
2. Install python:
	sudo apt-get install python2.7-dev
	sudo apt-get install python-pip
3. Install library:	
	pip install RPi.GPIO
	mkdir SPI-py
	cd SPI-py
	git clone https://github.com/lthiery/SPI-Py.git
	cd SPI-Py
	sudo python setup.py install
4. Install plugin:
	Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
	or manually using this URL:
    https://github.com/photo-mickey/OctoPrint-Filamentnfc/archive/master.zip

## Configuration

