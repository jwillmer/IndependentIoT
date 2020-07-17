#!/usr/bin/python
# -*- coding:utf-8 -*-
import logging
from data import Data
from utils import sendDataToThingerIO, writeToCSV, shutdown
from lipo import getLiPoPercentage

#logging.basicConfig(level=logging.DEBUG, format="%(asctime)s:%(levelname)s:%(message)s")
logging.basicConfig(level=logging.WARNING, format="%(asctime)s:%(levelname)s:%(message)s")

def is_intstring(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def main():       
    try:       
        logging.info(">> Collecting data") 
        data = Data()    
        
        logging.info(">> Writing data to CSV")  
        writeToCSV(data)

        logging.info(">> Sending data to Thinger.io")  
        sendDataToThingerIO(data)

        logging.info(">> Checking battery state")  
        if data.BatteryLevel < 20:
            logging.warning(f"Battery critical: {data.BatteryLevel}% - Shutdown initiated.")  
            shutdown()
        else:
            logging.info(f"Battery state: {data.BatteryLevel}%") 
        
    except IOError as e:
        logging.error(e)
        
    except KeyboardInterrupt:    
        logging.info("Script closed by user")
        exit()

if __name__ == "__main__":
        main()
