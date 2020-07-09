# sudo i2cdetect -y 1

from smbus2 import SMBus
import time
 
SHT31_ADDRESS = 0x45

# Get I2C bus
bus = SMBus(1)
 
# SHT31
bus.write_i2c_block_data(SHT31_ADDRESS, 0x2C, [0x06])

time.sleep(0.5)
 
# Read data back from 0x00(00), 6 bytes
# Temp MSB, Temp LSB, Temp CRC, Humididty MSB, Humidity LSB, Humidity CRC
data = bus.read_i2c_block_data(SHT31_ADDRESS, 0x00, 6)
 
# Convert the data
temp = data[0] * 256 + data[1]
cTemp = -45 + (175 * temp / 65535.0)
fTemp = -49 + (315 * temp / 65535.0)
humidity = 100 * (data[3] * 256 + data[4]) / 65535.0
 
# Output data to screen
print ("Temperature in Celsius is : %.2f C" %cTemp)
print ("Temperature in Fahrenheit is : %.2f F" %fTemp)
print ("Relative Humidity is : %.2f %%RH" %humidity)
