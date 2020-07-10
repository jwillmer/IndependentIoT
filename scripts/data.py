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
from dotenv import load_dotenv
load_dotenv(override=True)

class PowerLevel:
    def __init__(self, title, voltage, power, current, shunt_voltage):
        self.title = title
        self.voltage = voltage
        self.power = power
        self.current = current
        self.shunt_voltage = shunt_voltage


class Data:
    def __init__(self):       
         # Get first power levels before we activate other sensors
        self.powerLevel1, self.powerLevel2, self.powerLevel3, self.powerLevel4 = getPowerLevels()
        self.ip = socket.gethostbyname(socket.gethostname())
        self.timestamp = time.localtime()
        self.time = time.strftime('%H:%M:%S', self.timestamp)
        self.date = time.strftime("%Y-%m-%d", self.timestamp)
        self.uptime = time.strftime('%H:%M:%S', time.localtime(uptime()))
        self.connectionStatus = isOnline()
        self.temp, self.humidity = getTempAndHumidityData()

def getPowerLevels():    
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

    powerLevel1 = PowerLevel("Pi", ina1.bus_voltage, ina1.power, ina1.current, ina1.shunt_voltage)       
    powerLevel2 = PowerLevel("Battery", ina2.bus_voltage, ina2.power, ina2.current, ina2.shunt_voltage)
    powerLevel3 = PowerLevel("Solar", ina3.bus_voltage, ina3.power, ina3.current, ina3.shunt_voltage)
    powerLevel4 = PowerLevel("Undefined", ina4.bus_voltage, ina4.power, ina4.current, ina4.shunt_voltage)
    
    i2c_bus.deinit()
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
    if not os.getenv("WRITE_TO_CSV"): return

    logging.info("write data to csv")
    fileName = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'sensor-data.csv') 
    csv_file = Path(fileName)
    fileExists = csv_file.is_file()

    with open(fileName, 'a') as f:
        csv_writer = csv.writer(f, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            
        if not fileExists:
            csv_writer.writerow(['date', 'time', 'connectionStatus', 'ip', 'uptime', 'temp', 'humidity',
            'powerLevel1.title', 'powerLevel1.voltage', 'powerLevel1.power', 'data.powerLevel1.current', 'data.powerLevel1.shunt_voltage',
            'powerLevel2.title', 'powerLevel2.voltage', 'powerLevel2.power', 'data.powerLevel2.current', 'data.powerLevel2.shunt_voltage',
            'powerLevel3.title', 'powerLevel3.voltage', 'powerLevel3.power', 'data.powerLevel3.current', 'data.powerLevel3.shunt_voltage',
            'powerLevel4.title', 'powerLevel4.voltage', 'powerLevel4.power', 'data.powerLevel4.current', 'data.powerLevel4.shunt_voltage'])

        csv_writer.writerow([data.date, data.time, data.connectionStatus, data.ip, data.uptime, data.temp, data.humidity, 
        data.powerLevel1.title, data.powerLevel1.voltage, data.powerLevel1.power, data.powerLevel1.current, data.powerLevel1.shunt_voltage,
        data.powerLevel2.title, data.powerLevel2.voltage, data.powerLevel2.power, data.powerLevel2.current, data.powerLevel2.shunt_voltage,
        data.powerLevel3.title, data.powerLevel3.voltage, data.powerLevel3.power, data.powerLevel3.current, data.powerLevel3.shunt_voltage,
        data.powerLevel4.title, data.powerLevel4.voltage, data.powerLevel4.power, data.powerLevel4.current, data.powerLevel4.shunt_voltage])

def sendDataToThingerIO(data):
    if not os.getenv("THINGER_IO_ACTIVE"): return

    logging.info("send data to thinger.io")   
    endpoint = os.getenv("THINGER_IO_ENDPOINT")
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
                "current": data.powerLevel1.current,
                "shunt_voltage": data.powerLevel1.shunt_voltage
            },
            {
                "title": data.powerLevel2.title,
                "voltage": data.powerLevel2.voltage,
                "power": data.powerLevel2.power,
                "current": data.powerLevel2.current,
                "shunt_voltage": data.powerLevel2.shunt_voltage
            },
            {
                "title": data.powerLevel3.title,
                "voltage": data.powerLevel3.voltage,
                "power": data.powerLevel3.power,
                "current": data.powerLevel3.current,
                "shunt_voltage": data.powerLevel3.shunt_voltage
            },
            {
                "title": data.powerLevel4.title,
                "voltage": data.powerLevel4.voltage,
                "power": data.powerLevel4.power,
                "current": data.powerLevel4.current,
                "shunt_voltage": data.powerLevel4.shunt_voltage
            }
        ]
    }
    headers = {
        'Content-type': 'application/json', 
        'Accept': 'text/plain', 
        'Authorization': os.getenv("THINGER_IO_AUTH")}
    resp = requests.post(endpoint, json=payload , headers=headers)
    logging.debug("Thinger.io status code: {0}".format(resp.status_code))