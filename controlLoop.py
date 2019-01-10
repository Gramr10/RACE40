from hcsr04 import DistSensor
from carControl import CarControl
from imageProcessing import ImageProcessing
from os import system
import traceback
from multiprocessing import Process

dsThread = DistSensor(15,100,16,18)
imThread = ImageProcessing(10,640,480)
vehControl = CarControl(1,0x04)

dsThread.start()
imThread.start()

try:
    while True:
        ftti = dsThread.getFilteredTimeToImpact()
        avgDist = dsThread.getAvgDistance()
        vehControl.updateThrottle(60)
        averageDirAngle = imThread.getAverageAngle()
        #max physical angle is about 25 degrees,
        #which means we should map -25 to 0 as 1-50 and 1-25 as 51 - 100
        if averageDirAngle is not None:
            if averageDirAngle < -25:
                averageDirAngle = -25
            elif averageDirAngle > 25:
                averageDirAngle = 25
            
            vehControl.updateDirection(50+(averageDirAngle*2))
        
        if ftti < 1:
            print("impact imminent")
            vehControl.updateThrottle(10) #apply brake
            time.sleep(1)
            vehControl.updateThrottle(50) #no command
            vehControl.updateThrottle(35) #reverse
            vehControl.updateThrottle(50) #no command
            vehControl.updateThrottle(35) #reverse
            time.sleep(0.5)
            
        elif ftti < 5:
            print("possible impact")
            vehControl.updateThrottle(50) #no command
except:
    dsThread.stop()
    imThread.stop()
    
    print(traceback.format_exc())
