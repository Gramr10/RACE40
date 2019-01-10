import smbus
import time
import struct
from threading import Thread

class CarControl(Thread):
    i2cBus = None # ex 1
    address = None # ex 0x04
    direction = 149
    throttle = 49
    def __init__(self, bus, addr):
        self.i2cBus = smbus.SMBus(bus)
        self.address = addr

    def updateDirection(self,value):
        if value < 100:
            value = value+100
            self.direction = value
        else:
            self.direction = 149

    def updateThrottle(self,value):
        if value < 100:
            self.throttle = value
        else:
            self.throttle = 49
    
    def run(self):
        self.done = False
        while(True):
            try:
                self.i2cBus.write_byte(self.address, int(self.throttle))
                self.i2cBus.write_byte(self.address, int(self.direction))
            except:
                print("i2c error")
            time.sleep(.02) # 20 milliseconds cyclic


    def stop(self):
        self.done = True
