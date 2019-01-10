from threading import Thread
import time
import collections
import RPi.GPIO as GPIO
import traceback


class SensorEntry:
    time = time.time()
    data = 0.0
    def __init__(self,data,time):
        self.data = data
        self.time = time
    def __str__(self):
        return str(self.data)+" : "+str(self.time)+"\n"

    
class DistSensor(Thread):
    limit = 100.0 # distance limit
    buffLen = 0 # number of values to keep as history
    valBuff = None # buffer of historic values
    timeToImpact = 10 # time to impact in seconds
    trigger = 16 # trigger pin
    echo = 18 #echo pin
    lastFilteredDist = 0.0 # last calculated filtered distance
    lastFilteredTTI = 10 # last calculated filtered time to impact
    filteredValBuff = None # buffer of filtered values
    ttiBuff = None # buffer of time to impact values in seconds
    ttiBuffLen = 0 # number of time to impact values to keep as history
    done = False # Boolean which represents the state of the thread (running/done)
    valBuffLocked = False # Semaphore state for access to the value buffer
    filteredValBuffLocked = False # Semaphore state for access to the filtered value buffer

    def __init__(self,buffLen,limit,trig,echo):
        self.buffLen = buffLen
        self.valBuff = collections.deque(self.buffLen*[SensorEntry(self.limit,time.time())])
        self.filteredValBuff = collections.deque(self.buffLen*[SensorEntry(self.limit,time.time())])
        self.ttiBuffLen = 4*self.buffLen
        self.ttiBuff = collections.deque(self.ttiBuffLen*[10.0])
        self.limit = limit
        self.trigger = trig
        self.echo = echo
        super(DistSensor,self).__init__()

    def getTimeToImpact(self):
        #faster than getFilteredTimeToImpact, only takes the last two sensor values into the calculation
        crtMax = 0
        listMax = 0
        lst = []
        dataDif = 0
        timeDif = 0.0
        tti = None
        while self.valBuffLocked is True: #semaphore check for buffer access
            pass
        self.valBuffLocked = True
        for se in reversed(self.valBuff): #iterate over historic distance values, newest first
            if (se.data > crtMax) and (listMax <= 1): #only add two elements to the list
                lst.append(se)
                crtMax = se.data
                listMax = listMax+1
            else:
                break
        crtMin = self.limit
        self.valBuffLocked = False

        if listMax > 1:         
            for se in reversed(lst): #get the last two values detected by the sensor
                #print(str(se.data)+":"+str(se.time))
                dataDif = abs(se.data - dataDif)
                timeDif = abs(se.time - timeDif)
                if se.data < crtMin:
                    crtMin = se.data

            #print("dataDif:"+str(dataDif))
            #print("timeDif:"+str(timeDif))
            oneDistUnitTime = timeDif / dataDif
            tti = oneDistUnitTime * crtMin

        return tti


    def calculateFilteredTimeToImpact(self):
        #weighted and filtered time to impact (older values count less towards the average)
        crtMinData = self.limit * 1.0
        crtMaxData = 0
        crtMinTime = 0
        crtMaxTime = 0
        lst = []
        prevEntry = None
        dataDif = 0.0
        timeDif = 0.0
        tti = 10
        ttiList = []
        nrOfDecreasing = 0

        while self.filteredValBuffLocked is True:
            pass
        self.filteredValBuffLocked = True
        for se in reversed(self.filteredValBuff):
            if prevEntry is None:
                prevEntry = se
                if crtMinData > se.data:
                    crtMinData = se.data
            else:
                if se.data > prevEntry.data:
                    nrOfDecreasing = nrOfDecreasing + 1
                    #print("se.data: "+str(se.data)+" prevEntry.data: "+str(prevEntry.data))
                    dDif = se.data - prevEntry.data
                    tDif = prevEntry.time - se.time
                    dataDif = dDif + dataDif 
                    timeDif = tDif + timeDif
                    if crtMinData > se.data:
                        crtMinData = se.data
                            
                    if nrOfDecreasing >= (len(self.filteredValBuff) / 4):
                        #if values are mostly decreasing, then
                        #timeToImpact should be relevant
                        #print(str(dataDif/nrOfDecreasing)+" - "+str(timeDif/nrOfDecreasing)+" crtMin: "+str(crtMinData))
                        if dataDif > 1:
                            dataDif = dataDif/nrOfDecreasing
                            timeDif = timeDif/nrOfDecreasing
                            tti = ((timeDif * crtMinData) / dataDif)
                            

                prevEntry = se
        self.filteredValBuffLocked = False
        if self.lastFilteredDist > 5:
            self.timeToImpact = (self.timeToImpact + tti) / 2
        else:
            self.timeToImpact = 0    
        self.ttiBuff.append(self.timeToImpact)
        self.ttiBuff.popleft()
        
        sum = 0
        for nr in self.ttiBuff:
            sum = sum + nr
            
        self.lastFilteredTTI = sum / self.ttiBuffLen
        return self.lastFilteredTTI


    def getFilteredTimeToImpact(self):
        return self.lastFilteredTTI
    
    def getAvgDistance(self):
        #weighted and filtered distance (older values count less towards the average)
        sumDist = 0
        invalid = 0
        index = 0
        
        validLen = len(self.valBuff)
        if validLen > 0:
            while self.valBuffLocked is True:
                pass
            self.valBuffLocked = True
            for se in reversed(self.valBuff):
                if se.data >= 0:
                    index = index + 1               
                    sumDist = sumDist + se.data
                else:
                    validLen = validLen - 1
            self.valBuffLocked = False
            self.lastFilteredDist = sumDist/validLen
            while self.filteredValBuffLocked is True:
                pass
            self.filteredValBuffLocked = True
            self.filteredValBuff.append(SensorEntry(self.lastFilteredDist,time.time()))
            self.filteredValBuff.popleft()
            self.filteredValBuffLocked = False
            return self.lastFilteredDist
        return self.limit
    

    def measureDistance(self):
        c= 0
        distance = self.limit
        GPIO.output(self.trigger, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(self.trigger, GPIO.LOW)
        
        while GPIO.input(self.echo)==0:
            #print("while1")
            if c > 60:
                #print("Distance: "+str(distance) +"cm")
                while self.valBuffLocked is True:
                    pass
                self.valBuffLocked = True
                self.valBuff.append(SensorEntry(distance,time.time()))
                self.valBuff.popleft()
                self.valBuffLocked = False
                return
            c= c+1
            pulse_start_time = time.time()
            while GPIO.input(self.echo)==1:
                pulse_end_time = time.time()
                pulse_duration = pulse_end_time - pulse_start_time
                distance = round(pulse_duration * 17150, 2)
                if(distance > 100):
                    #print("Distance: "+str(distance) +"cm")
                    while self.valBuffLocked is True:
                        pass
                    self.valBuffLocked = True
                    self.valBuff.append(SensorEntry(self.limit,time.time()))
                    self.valBuff.popleft()
                    self.valBuffLocked = False
                    return

    def debugAdd(self,value,time):
        self.valBuff.append(SensorEntry(value,time))
        self.valBuff.popleft()
        
    def run(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.trigger, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)
        GPIO.output(self.trigger, GPIO.LOW)
        self.done = True
        try:
            while self.done is False:
                self.measureDistance()
                self.calculateFilteredTimeToImpact()
                time.sleep(0.01)
                #print("Distance: "+str(self.getAvgDistance()) +"cm")		
        except:
            print(traceback.format_exc())
            self.stop()

        
    
    def stop(self):
        self.done = True
        GPIO.cleanup()

    def __str__(self):
        sr = ""
        for se in self.valBuff:
            sr = sr + str(se)
        return sr

