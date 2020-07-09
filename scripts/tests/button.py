import RPi.GPIO as GPIO 
import threading
import time
from signal import signal, SIGINT

buttonPin = 33
result_available = threading.Event()

def emptyThread():
    print("running")

def button_callback(channel):
    print("Button was pushed!")

def handler(signal_received, frame):
    GPIO.cleanup()
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    exit(0)

def main():    
    signal(SIGINT, handler)

    thread = threading.Thread(target=emptyThread)
    thread.start()

    GPIO.setmode(GPIO.BOARD) 
    GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)     
    GPIO.add_event_detect(buttonPin,GPIO.RISING,callback=button_callback) 

    result_available.wait()


if __name__ == '__main__':
    main()