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
     sudo apt-get install python3 python3-pip
     sudo pip3 install numpy scikit-image picamera
'''
import numpy as np # Linear algebra and matrix operations
from skimage import io, color # Image processing tools
from picamera import PiCamera # Interface with PiCamera module
from picamera.array import PiRGBArray # Handle PiCamera image frames as RGB m-by-n-by-3 arrays
from pivideostream import PiVideoStream # Open camera video stream on separate thread
import time # Timekeeping and labelling
import threading # Parallelizing tasks
import queue # Allow processing on captured frames as they are saved
import logging # Log messages and information
import os # Manage files and directories

class FrameReader():
    ''' Samples frames from a pi video stream and saves them to disk.
    '''
    def __init__(self,stream,q):
        # super(FrameReader,self).__init__()
        self.stream = stream
        self.q = q
        self.stopped = True

    def run(self):
        logging.debug('started FrameReader')
        while not self.stopped:
            frame=self.stream.read() # sample from stream
            framename=str(int(time.time()*10000000)) # name image based on time sampled
            io.imsave('raw/'+framename+'.jpg',frame) # save to disk as jpg
            if not self.q.full():
                self.q.put((frame,framename)) # send frame to mask processing queue 
            else: logging.debug('Queue is full ('+str(self.q.qsize())+'frames)')
        return

    def start(self):
        self.stopped = False
        self.t = threading.Thread(target=self.run, args=(), name='reader')
        self.t.daemon = True
        self.t.start()

    def stop(self):
        self.stopped = True
        self.t.join()
        logging.debug('stopped FrameReader')

class FrameMasker(threading.Thread):
    ''' Masks frames from the queue and saves the mask to disk.
    '''
    def __init__(self,stream,q):
        # super(FrameMasker,self).__init__()
        self.stream=stream
        self.q=q
        self.stopped = True

    def run(self):
        logging.debug('started FrameMasker')
        while not self.stopped:
            if not self.q.empty():
                (frame, framename) = self.q.get() # retrieve frame from queue (First In Last Out)
                # frame = resize(frame, width=256)
                mask = get_hsv_mask(frame) # get hsv logical mask
                io.imsave('mask/'+framename+'.jpg',mask) # save image to disk
            # else: logging.debug('Queue is empty!')

    def start(self):
        self.stopped = False
        self.t = threading.Thread(target=self.run, args=(), name='masker')
        self.t.daemon = True
        self.t.start()

    def stop(self):
        logging.debug('masking remaining frames...')
        while(True):
            if self.q.empty():
                self.stopped = True
                self.t.join()
                logging.debug('stopped FrameMasker')
                break

def hsv_mask(img, limits):
    ''' Generate binary logical mask to filter RGB image to a range of HSV values (inclusive)
          inputs:
            img     as  PIL image object
            limits  as  tuple of two [Hue, Saturation, Value] lists or arrays
    '''
    hsv = color.rgb2hsv(img) # transform RGB to HLS
    lower_limit, upper_limit = limits[0], limits[1]
    mask = np.zeros_like(hsv)
    mask_lower = mask
    mask_upper = mask
    for i in range(3):
        mask_lower[:,:,i] = (hsv[:,:,i] >= lower_limit[i])
        mask_upper[:,:,i] = (hsv[:,:,i] <= upper_limit[i])
    mask = np.logical_and(mask_lower,mask_upper)
    return mask

def get_hsv_mask(img):
    ''' Generate a binary logical mask to filter by a Hue-Lightness-Saturation range.
    '''
    color_range = ([35, 5, 35], [120, 140, 255])
    mask = hsv_mask(img, color_range)
    return mask

def stopAll(stream,reader,masker):
    reader.stop()
    stream.stop()
    masker.stop()
    return

def init():
    ''' Run hardware and software system checks.
    '''
    logging.basicConfig(level=logging.DEBUG,
                        format='(%(threadName)-9s) %(message)s',)
    logging.debug(' --- Where U At Plants? --- ')
    logging.debug('performing startup and system checks:')
    try:
        # check for directory structure
        if os.path.exists('raw'):
            logging.debug('  found directory: raw')
        else:
            os.mkdir('raw')
            logging.debug('  created directory: raw')
        if os.path.exists('mask'):
            logging.debug('  found directory: mask')
        else:
            os.mkdir('mask')
            logging.debug('  created directory: mask')
    except:
        logging.debug('[NO GO] file directories')
        return False
    logging.debug('[GO] file directories')

    try:
        # check video stream
        teststream = PiVideoStream(resolution=(640,480),framerate=60).start()
        logging.debug('  (spooling PiVideoStream...)')
        time.sleep(2)
        testframe = teststream.read()
        teststream.stop()
    except:
        teststream.stop()
        logging.debug('[NO GO] PiVideoStream')
        return False
    logging.debug('[GO] PiVideoStream')
    logging.debug('  (restarting PiVideoStream...)')
    teststream.start()
    time.sleep(2)
    try:
        # check FrameReader
        testq=queue.Queue()
        testreader,testmasker = FrameReader(stream=teststream,q=testq), FrameMasker(stream=teststream,q=testq)
        testreader.start()
        logging.debug('  (spooling FrameReader...)')
        time.sleep(1)
        testreader.stop()
    except:
        testreader.stop()
        logging.debug('[NO GO] FrameReader')
        return False
    logging.debug('[GO] FrameReader')
    teststream.stop()

    try:
        # check FrameMasker
        testmasker.start()
        logging.debug('  (spooling FrameMasker...)')
        time.sleep(1)
        testmasker.stop()
    except:
        logging.debug('[NO GO] FrameMasker')
        testmasker.stop()
        return False
    logging.debug('[GO] FrameMasker')

    logging.debug('All systems go!')
    return True

if __name__ == '__main__':
    if not init():
        logging.debug('ABORTING STARTUP')
        exit()
    q = queue.Queue()
    resolution=(640,480) # http://picamera.readthedocs.io/en/release-1.10/fov.html
    framerate=60
    logging.debug('started threaded video stream ('+str(resolution)+','+str(framerate)+' fps)')
    stream = PiVideoStream(resolution=resolution,framerate=framerate).start()
    for i in reversed(range(1,4)):
        logging.debug('starting capture & processing in '+str(i)+' seconds')
        time.sleep(1)
    reader,masker=FrameReader(stream=stream,q=q),FrameMasker(stream=stream,q=q)
    reader.start()
    masker.start()

    while(True):
        user_input = input('Stop the stream?: ')
        if user_input:
            stopAll(stream,reader,masker)
            break
