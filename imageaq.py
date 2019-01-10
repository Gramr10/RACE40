from threading import Thread
import time
import collections
from picamera import PiCamera
from picamera.array import PiRGBArray
import traceback
import cv2

class ImageAcquisition(Thread):
    lastImage = None
    #imageWriteLock = False
    theta=0
    camera = PiCamera()
    rawCapture = None
    done = False
    init_learn = False

    def __init__(self,res,framerate):
       
        self.camera.resolution = res
        self.camera.framerate = framerate
        self.rawCapture = PiRGBArray(self.camera, size=res)
        super(ImageAcquisition,self).__init__()

    def run(self):
        self.done = False
        try:
            for frame in self.camera.capture_continuous(self.rawCapture,format='bgr', use_video_port=True):
                #while self.imageWriteLock is True:
                    #pass
                #self.imageWriteLock = True
                #print("in continuous capture")
                self.lastImage = frame.array
                #self.imageWriteLock = False
                self.rawCapture.truncate(0)
                if self.done is True:
                    break;
                
        except:
            print(traceback.format_exc())
            cv2.imshow("crashed on image",self.lastImage)
            self.stop()

    def stop(self):
        self.done = True
        
    def getLastImage(self):
        #while self.imageWriteLock is True:
        #    pass
        return self.lastImage

#This second Thread is created in order to run on a second processor. We will want to invoke the multiprocessing mechanism to assign this Thread to any other processor, in order to solve
#the issue where the camera would be slowed down by any other processing (thus not be able to take as many camera captures as the camera allows physically)
#class recordToLearn(Thread):
#
#    #To-Do: Where should this thread by invoked? Within the controlLoop module, or within imageProcessing?
#    #To-Do: How should this thread receive the init_learn parameter? Would it receive via controlLoop?
#
#    camera = PiCamera()
#
#    def __init__(self, init_learn):
#        self.init_learn = init_learn
#        self.camera.resolution = res
#        self.camera.framerate = framerate
#        super(recordToLearn,self).__init__()
#        
#    def run(self):
#        if self.init_learn == True:
#            try:
#                for i, frame in enumerate(self.camera.capture_continuous('cameraCapture/' + '{i}.jpg', format='jpeg', use_video_port=True)):
#                    if self.init_learn is False:
#                        break;
#                    
#            except:
#                print(traceback.format_exc())
#                self.stop()
#
#    def stop(self):
#        self.init_learn = False


#This is the function variant of the Thread from above
#def recordToLearn(init_learn):
#    camera = PiCamera()
#    if self.init_learn == True:
#        self.camera.resolution = (640,480)
#        self.camera.framerate = 40
#        try:
#            for i, frame in enumerate(self.camera.capture_continuous('cameraCapture/' + '{i}.jpg', format='jpeg', use_video_port=True)):
#                print('Testing')
#                if self.init_learn is False:
#                    break;
#                
#        except:
#            print(traceback.format_exc())
#            self.stop()
