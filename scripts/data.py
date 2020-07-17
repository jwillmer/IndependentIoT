import logging
import socket
import time
import traceback
from contextlib import closing

import board
from adafruit_ina219 import INA219, ADCResolution, BusVoltageRange
from smbus2 import SMBus
from uptime import uptime


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
        self.uptime = time.strftime('%H:%M:%S', time.gmtime(uptime()))
        self.connectionStatus = isOnline()
        self.temp, self.humidity = getTempAndHumidityData()

def getPowerLevels():       
    dic = {
        0x40: "Pi",
        0x41: "Battery",
        0x42: "Solar",
        0x43: "Unknown"
    }

    i2c_bus = board.I2C()

    for address in dic: 
        ina = INA219(i2c_bus,addr=address)
        ina.bus_adc_resolution = ADCResolution.ADCRES_12BIT_32S
        ina.shunt_adc_resolution = ADCResolution.ADCRES_12BIT_32S
        ina.bus_voltage_range = BusVoltageRange.RANGE_16V
        yield PowerLevel(dic[address], ina.bus_voltage, ina.power, ina.current, ina.shunt_voltage) 

    i2c_bus.deinit()


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
