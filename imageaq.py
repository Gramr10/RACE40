from threading import Thread
import time
import collections
from picamera import PiCamera
from picamera.array import PiRGBArray
import traceback
import cv2
import io

class ImageAcquisition(Thread):
    lastImage = None
    theta=0
    camera = PiCamera()
    rawCapture = None
    done = False
    learningMode = False
    outputs = [io.BytesIO() for i in range(40)]

    def __init__(self,res,framerate,learningActive):
       
        self.learningMode = learningActive #Trigger variable to start learning mode -> stores images in jpeg format until set to False
        self.camera.resolution = res
        self.camera.framerate = framerate
        self.rawCapture = PiRGBArray(self.camera, size=res)
        self.camera.shutter_speed = 400 #Under_Test: Delete or make this configurable within the controlLoop main module. Currently testing @ 400 microseconds, to increase the FPS.
        super(ImageAcquisition,self).__init__()

    def run(self):
        self.done = False
        try:
            #This case shall be used for neural network learning -> shall store images at the specified location, as long as in this mode.
            if self.learningMode == True:
                #Because it takes too much time to store the images from RAM to ROM (huge bottleneck), this mode will have to store the images strictly in RAM while another process will store the images in ROM concurrently.
                start = time.time()
                self.camera.capture_sequence(self.outputs, format='jpeg', use_video_port=True)
                finish = time.time()
                self.camera.close()
                print('Captured 40 images at %.2ffps' % (40/(finish-start))) #Delete this line when parallel storing process has been implemented. Currently, can take over 40 FPS, in stream (RAM).
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
