import smbus
import time
import struct

        
i2cBus = smbus.SMBus(1)
address = 0x04  
while True:
    var = input("Enter value for I2C transmission (1 byte, decimal): \n")
    i2cBus.write_byte(address, int(var))

