import os
import logging
import time
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
        self.powerLevel1, self.powerLevel2, self.powerLevel3, self.powerLevel4 = getPowerLevels()

def getPowerLevels():    
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

    powerLevel1 = PowerLevel("Solar", ina1.bus_voltage, ina1.power, ina1.current)       
    powerLevel2 = PowerLevel("Battery", ina2.bus_voltage, ina2.power, ina2.current)
    powerLevel3 = PowerLevel("Pi", ina3.bus_voltage, ina3.power, ina3.current)
    powerLevel4 = PowerLevel("Undefined", ina4.bus_voltage, ina4.power, ina4.current)

    return powerLevel1, powerLevel2, powerLevel3, powerLevel4


def check_socket(host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        if sock.connect_ex((host, port)) == 0:
            return 1
        else:
            return 0

def isOnline():
    return "Connected" if check_socket('8.8.8.8', 53) else "Offline"          

def getTempAndHumidityData():
    SHT31_ADDRESS = 0x45
    bus = SMBus(1) 
    bus.write_i2c_block_data(SHT31_ADDRESS, 0x2C, [0x06])
    time.sleep(0.25)
    data = bus.read_i2c_block_data(SHT31_ADDRESS, 0x00, 6)
    bus.close()
    rawTemp = data[0] * 256 + data[1]
    temp = -45 + (175 * rawTemp / 65535.0)
    humidity = 100 * (data[3] * 256 + data[4]) / 65535.0
    return temp, humidity

def writeToCSV(data):
    logging.info("write data to csv")
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
    logging.info("send data to thinger.io")
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
    logging.debug("Thinger.io status code: {0}".format(resp.status_code))