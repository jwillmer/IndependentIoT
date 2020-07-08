#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in9
from PIL import Image,ImageDraw,ImageFont
import RPi.GPIO as GPIO 
import threading
import time
from signal import signal, SIGINT
from data import Data


#logging.basicConfig(level=logging.DEBUG, format="%(asctime)s:%(levelname)s:%(message)s")
logging.basicConfig(level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s")

# Init button
buttonPin = 13
result_available = threading.Event()

# Init screen
MAX_W, MAX_H = 128, 296
current_height = 0
font14 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 14)
font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)

def writeInfo(draw, title, value):
    global current_height
    draw.text((0, current_height), title, font = font14, fill = 0)
    w, h = draw.textsize(value, font=font14)
    draw.text((MAX_W - w, current_height), value, font = font14, fill = 0)
    current_height = current_height + 14


def writePowerLevels(draw, title, voltage, power, current):
    global current_height
    draw.text((0, current_height+10), title, font = font18, fill = 0)
    current_height = current_height + 28

    writeInfo(draw, 'Voltage:', "{:4.3f}V".format(voltage))
    writeInfo(draw, 'Current:', "{:5.2f}mA".format(current))
    writeInfo(draw, 'Power:', "{:4.3f}W".format(power))

def emptyThread():
    logging.info("emptyThread running")

def buttonPressed(channel):
    logging.info(">> button press detected!")
    updateScreen()

def updateScreen():
    logging.info(">> updating screen")
    global current_height

    logging.info("collect data")
    data = Data()

    logging.info("clear screen")
    epd = epd2in9.EPD()
    MAX_W, MAX_H = epd.width, epd.height   
    epd.init(epd.lut_full_update)      

    logging.info("write data to screen")
    image = Image.new('1', (epd.width, epd.height), 255)    
    draw = ImageDraw.Draw(image)    
    
    writeInfo(draw, 'Time:', data.time)
    writeInfo(draw, 'Uptime:', data.uptime)
    writeInfo(draw, 'Online:', data.connectionStatus)
    writeInfo(draw, 'IP:', data.ip)
    writeInfo(draw, 'Temp:', "{:.2f}C".format(data.temp))
    writeInfo(draw, 'Humidity:', "{:.2f}%".format(data.humidity))
    
    writePowerLevels(draw, data.powerLevel1.title, data.powerLevel1.voltage, data.powerLevel1.power, data.powerLevel1.current)   
    writePowerLevels(draw, data.powerLevel2.title, data.powerLevel2.voltage, data.powerLevel2.power, data.powerLevel2.current)   
    writePowerLevels(draw, data.powerLevel3.title, data.powerLevel3.voltage, data.powerLevel3.power, data.powerLevel3.current)   
    
    image = image.transpose(Image.ROTATE_180) 
    epd.display(epd.getbuffer(image))
    epd.sleep()
    current_height=0  
    logging.info("<< screen updated")  

def handler(signal_received, frame):
    GPIO.cleanup()
    logging.info("SIGINT or CTRL-C detected. Exiting gracefully")
    exit(0)

def main():    
    signal(SIGINT, handler)

    thread = threading.Thread(target=emptyThread)
    thread.start()

    logging.info(">> listening for button press..")
    GPIO.setmode(GPIO.BCM) 
    GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)     
    GPIO.add_event_detect(buttonPin,GPIO.RISING,callback=buttonPressed) 

    result_available.wait()


if __name__ == '__main__':
    main()
