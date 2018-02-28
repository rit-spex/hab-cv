'''
 Where U At Plants?
 Author:       Philip Linden
 Date Created: February 27, 2018
 Description:
     Primary Objective:   Save single frames from a Raspberry Pi 3 camera video stream.
     Secondary Objective: Apply a binary mask to filter the image frame to highlight vegetation.
                          - Filter by "greenish" hues if using a standard PiCamera
                          - Filter by a threshold grayscale response if using a PiCamera NOIR
 Dependencies:
     sudo pip3 install numpy picamera pillow imutils
'''
from PIL import Image # Basic image processing tools
from PIL import ImageColor # Color transformation tools
from picamera import PiCamera # Interface with PiCamera module
from picamera.array import PiRGBArray # Handle PiCamera image frames as RGB m-by-n-by-3 arrays
from imutils.video.pivideostream import PiVideoStream # Open camera video stream on separate thread
import numpy as np # Linear algebra and matrix operations
import time # Timekeeping and labelling
import threading # Parallelizing tasks
import queue # Allow processing on captured frames as they are saved
import logging # Log messages and information

class FrameReader():
    ''' Samples frames from a pi video stream and saves them to disk.
    '''
    def __init__(self):
        super(FrameReader,self).__init__()
        self.stopped = True

    def run(self):
        logging.debug('started FrameReader')
        while not self.stopped:
            frame=stream.read() # sample from stream
            framename=str(int(time.time()*10000000)) # name image based on time sampled
            cv2.imwrite('raw/'+framename+'.jpg',frame) # save to disk as jpg
            if not q.full():
                q.put((frame,framename)) # send frame to mask processing queue
            else: logging.debug('Queue is full ('+str(q.qsize())+'frames)')
        return

    def start(self):
        self.stopped = False
        t = threading.Thread(target=self.run, args=(), name='reader')
        t.daemon = True
        t.start()

    def stop(self):
        self.stopped = True
        logging.debug('stopped FrameReader')


