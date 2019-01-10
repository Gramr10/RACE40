from picamera.array import PiRGBArray
import RPi.GPIO as GPIO
import time
import numpy as np
import math
import collections
from imageaq import ImageAcquisition
from threading import Thread
import cv2 

class ImageProcessing(Thread):
    running = False
    minLineLength = 10
    maxLineGap = 5
    valBuff = None
    h,w = None,None
    imgThread = None
    histAverage = None
    average = None
    history = None
    learningMode = False

    def __init__(self, history,h,w, learningActive):
        self.history = history
        self.valBuff = collections.deque(history*[0])
        self.h = h
        self.w = w
        self.learningMode = learningActive
        self.imgThread = ImageAcquisition((h,w),60, learningActive)        
        super(ImageProcessing,self).__init__()
    
    def getAverageAngleInstant(self):
        return self.average
        
    def getAverageAngle(self):
        return self.histAverage
        
    def showImage(self,frameName,image):
        cv2.imshow(frameName,image)
        key = cv2.waitKey(1) & 0xFF
    
    def run(self):
        self.running = True
        self.imgThread.start()
        time.sleep(0.5)
        while self.running:
            frameTime = time.time()
            if self.learningMode == False:
                image = self.imgThread.getLastImage()

            #neural network function goes here
            #it should return the angle required for steering
            #and a value for throttle
            #self.showImage("Frame",image)
                print(image)
            #The below line should record what the camera sees as a video file

                frameTime = time.time() - frameTime
                frameTime = 1/frameTime
                print("FPS: " + str(frameTime))
    def stop(self):
        self.running = False



