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
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
from uptime import uptime
import socket
from contextlib import closing
import board
from adafruit_ina219 import ADCResolution, BusVoltageRange, INA219
from smbus2 import SMBus
from pathlib import Path
import csv
import requests

#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)

# Init screen
MAX_W, MAX_H = 128, 296
current_height = 0
font14 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 14)
font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)

# Init SHT30 temp and humidity sensor
SHT31_ADDRESS = 0x45
bus = SMBus(1)

# Init power hat
i2c_bus = board.I2C()

ina1 = INA219(i2c_bus,addr=0x40)
ina2 = INA219(i2c_bus,addr=0x41)
ina3 = INA219(i2c_bus,addr=0x42)
ina4 = INA219(i2c_bus,addr=0x43)

ina1.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina1.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina1.bus_voltage_range = BusVoltageRange.RANGE_16V

ina2.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina2.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina2.bus_voltage_range = BusVoltageRange.RANGE_16V

ina3.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina3.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina3.bus_voltage_range = BusVoltageRange.RANGE_16V

ina4.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina4.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
ina4.bus_voltage_range = BusVoltageRange.RANGE_16V

class PowerLevel:
    def __init__(self, title, voltage, power, current):
        self.title = title
        self.voltage = voltage
        self.power = power
        self.current = current


class Data:
    def __init__(self):
        self.ip = socket.gethostbyname(socket.gethostname())
        self.timestamp = time.localtime()
        self.time = time.strftime('%H:%M:%S', self.timestamp)
        self.date = time.strftime("%Y-%m-%d", self.timestamp)
        self.uptime = time.strftime('%H:%M:%S', time.localtime(uptime()))
        self.connectionStatus = isOnline()
        self.temp, self.humidity = getTempAndHumidityData()
        self.powerLevel1 = PowerLevel("Solar", ina1.bus_voltage, ina1.power, ina1.current)       
        self.powerLevel2 = PowerLevel("Battery", ina2.bus_voltage, ina2.power, ina2.current)
        self.powerLevel3 = PowerLevel("Pi", ina3.bus_voltage, ina3.power, ina3.current)
        self.powerLevel4 = PowerLevel("Undefined", ina4.bus_voltage, ina4.power, ina4.current)




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

    writeInfo(draw, 'Voltage:', "{:6.3f}V".format(voltage))
    writeInfo(draw, 'Power:', "{:9.6f}W".format(power))
    writeInfo(draw, 'Current:', "{:9.6f}A".format(current))

def check_socket(host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        if sock.connect_ex((host, port)) == 0:
            return 1
        else:
            return 0

def isOnline():
    return "Connected" if check_socket('8.8.8.8', 53) else "Offline"          

def getTempAndHumidityData():
    global bus
    bus.write_i2c_block_data(SHT31_ADDRESS, 0x2C, [0x06])
    time.sleep(0.25)
    data = bus.read_i2c_block_data(SHT31_ADDRESS, 0x00, 6)
    rawTemp = data[0] * 256 + data[1]
    temp = -45 + (175 * rawTemp / 65535.0)
    humidity = 100 * (data[3] * 256 + data[4]) / 65535.0
    return temp, humidity

def is_intstring(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def writeToCSV(data):
    logging.debug("write data to csv")
    fileName = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'sensor-data.csv') 
    csv_file = Path(fileName)
    fileExists = csv_file.is_file()

    with open(fileName, 'a') as f:
        csv_writer = csv.writer(f, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            
        if not fileExists:
            csv_writer.writerow(['date', 'time', 'connectionStatus', 'ip', 'uptime', 'temp', 'humidity',
            'powerLevel1.title', 'powerLevel1.voltage', 'powerLevel1.power', 'data.powerLevel1.current',
            'powerLevel2.title', 'powerLevel2.voltage', 'powerLevel2.power', 'data.powerLevel2.current',
            'powerLevel3.title', 'powerLevel3.voltage', 'powerLevel3.power', 'data.powerLevel3.current',
            'powerLevel4.title', 'powerLevel4.voltage', 'powerLevel4.power', 'data.powerLevel4.current'])

        csv_writer.writerow([data.date, data.time, data.connectionStatus, data.ip, data.uptime, data.temp, data.humidity, 
        data.powerLevel1.title, data.powerLevel1.voltage, data.powerLevel1.power, data.powerLevel1.current,
        data.powerLevel2.title, data.powerLevel2.voltage, data.powerLevel2.power, data.powerLevel2.current,
        data.powerLevel3.title, data.powerLevel3.voltage, data.powerLevel3.power, data.powerLevel3.current,
        data.powerLevel4.title, data.powerLevel4.voltage, data.powerLevel4.power, data.powerLevel4.current])

def sendDataToThingerIO(data):
    logging.debug("send data to thinger.io")
    endpoint = "https://backend.thinger.io/v3/users/jwillmer/devices/FreelancePi/callback/data"
    payload  = {
        "date": data.date,
        "time": data.time,
        "connectionStatus": data.connectionStatus,
        "ip": data.ip,
        "uptime": data.uptime,
        "temp": data.temp,
        "humidity": data.humidity,
        "powerLevels": [
            {
                "title": data.powerLevel1.title,
                "voltage": data.powerLevel1.voltage,
                "power": data.powerLevel1.power,
                "current": data.powerLevel1.current
            },
            {
                "title": data.powerLevel2.title,
                "voltage": data.powerLevel2.voltage,
                "power": data.powerLevel2.power,
                "current": data.powerLevel2.current
            },
            {
                "title": data.powerLevel3.title,
                "voltage": data.powerLevel3.voltage,
                "power": data.powerLevel3.power,
                "current": data.powerLevel3.current
            },
            {
                "title": data.powerLevel4.title,
                "voltage": data.powerLevel4.voltage,
                "power": data.powerLevel4.power,
                "current": data.powerLevel4.current
            }
        ]
    }
    headers = {
        'Content-type': 'application/json', 
        'Accept': 'text/plain', 
        'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJEZXZpY2VDYWxsYmFja19GcmVlbGFuY2VQaSIsInVzciI6Imp3aWxsbWVyIn0.eMPRRFtBM3wa0m2wF5S3bxFs1pi-NEuGRWuWOswhqho'}
    resp = requests.post(endpoint, json=payload , headers=headers)
    logging.debug(resp.status_code)

def main(sleep=5):  
    logging.info("Loop sleep set to {0} seconds".format(sleep))  
    logging.info("{0} - Starting loop".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
    
    try:       
        epd = epd2in9.EPD()
        MAX_W, MAX_H = epd.width, epd.height
                 
        while (True): 
            data = Data()
            global current_height
            epd.init(epd.lut_full_update)       
    
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
            
            writeToCSV(data)
            sendDataToThingerIO(data)
            logging.debug("{0} - Going to sleep for {1} seconds".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), sleep))
            time.sleep(sleep)
        
    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("{0} - Script closed by user:".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        epd2in9.epdconfig.module_exit()
        exit()

if __name__ == "__main__":
    arguments = sys.argv[1:]    

    if arguments:
        if not is_intstring(sys.argv[1]):
            sys.exit("Argument must be integer. Exit.")
        main(int(sys.argv[1]))
    else: 
        main()