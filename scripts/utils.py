import csv
import logging
import os
from pathlib import Path

import requests


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
