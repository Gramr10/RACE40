from threading import Thread
import time
import collections
from picamera import PiCamera
from picamera.array import PiRGBArray
import traceback
import cv2
import io
from PIL import Image
from threading import Thread, Semaphore
import numpy as np

class ImageAcquisition(Thread):
    lastImage = None
    theta=0
    camera = PiCamera()
    rawCapture = None
    done = False
    learningMode = False
    outputs = io.BytesIO()
    cameraAccess = Semaphore()
    count = 0
    t1 = None
    t2 = None

    def __init__(self,res,framerate,learningActive):
       
        self.learningMode = learningActive #Trigger variable to start learning mode -> stores images in jpeg format until set to False
        self.camera.resolution = res
        self.camera.framerate = framerate
        self.rawCapture = PiRGBArray(self.camera, size=res)
        self.camera.shutter_speed = 400 #Under_Test: Delete or make this configurable within the controlLoop main module. Currently testing @ 400 microseconds, to increase the FPS.
        self.t1 = Thread(target=self.captureLearn)
        self.t2 = Thread(target=self.storeLearn)
        super(ImageAcquisition,self).__init__()

    def run(self):
        self.done = False
        try:
            #This case shall be used for neural network learning -> shall store images at the specified location, as long as in this mode.
            if self.learningMode == True:
                #Because it takes too much time to store the images from RAM to ROM (huge bottleneck), this mode will have to store the images strictly in RAM while another process will store the images in ROM concurrently.
                self.t1.start()
                self.t2.start()
            #This case shall be used for online imageProcessing, that will decide when to steer and when to accelerate.
            if self.learningMode == False:
                for frame in self.camera.capture_continuous(self.rawCapture,format='bgr', use_video_port=True):
                    self.lastImage = frame.array
                    self.rawCapture.truncate(0)
                    if self.done is True:
                        break;
                
        except:
            print(traceback.format_exc())
            self.stop()

    def stop(self):
        self.done = True
        self.camera.close()
        
    def getLastImage(self):
        return self.lastImage

    def captureLearn(self):
        while True:
            self.cameraAccess.acquire()
            print('capturing')
            self.camera.capture(self.outputs, format='jpeg', use_video_port=True)
            self.cameraAccess.release()
            time.sleep(0.02)

    def storeLearn(self):
        while True:
            self.cameraAccess.acquire()
            print('storing')
            rawIO = self.outputs
            rawIO.seek(0)
            byteImg = Image.open(rawIO)
            self.count+=1
            filename = "cameraCapture/image" + str(self.count) + ".jpg"
            byteImg.save(filename, 'JPEG')
            self.cameraAccess.release()
            time.sleep(0.02)

