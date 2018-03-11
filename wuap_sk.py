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
import argparse # Command line options

class FrameReader():
    ''' Samples frames from a pi video stream and saves them to disk.
    '''
    def __init__(self,stream,q,testmode=False):
        # super(FrameReader,self).__init__()
        self.stream = stream
        self.q = q
        self.testmode=testmode
        if testmode: logger.info('testing mode enabled!')
        self.stopped = True

    def run(self):
        logger.debug('started FrameReader')
        while not self.stopped:
            frame=self.stream.read() # sample from stream
            framename=str(int(time.time()*10000000)) # name image based on time sampled
            if self.testmode: framename='TEST_'+framename
            try:
                io.imsave('raw/raw_'+framename+'.jpg',frame) # save to disk as jpg
            except Exception as e:
                logger.error('failed to save image: '+'raw/raw_'+framename+'.jpg')
                logger.error(e)
                self.stop()
                return
            logger.debug('{0} saved and added to queue in position {1}.'.format('raw_'+framename,str(self.q.qsize())))
            if not self.q.full():
                self.q.put((frame,framename)) # send frame to mask processing queue
            else: logger.debug('Queue is full! '+str(self.q.qsize())+' waiting...')
        return

    def start(self):
        self.stopped = False
        self.t = threading.Thread(target=self.run, args=(), name='reader')
        self.t.daemon = True
        self.t.start()

    def stop(self):
        self.stopped = True
        self.t.join()
        logger.debug('stopped FrameReader')

class FrameMasker(threading.Thread):
    ''' Masks frames from the queue and saves the mask to disk.
    '''
    def __init__(self,stream,q,irmode=False,testmode=False):
        # super(FrameMasker,self).__init__()
        self.stream=stream
        self.q=q
        self.testmode=testmode
        if testmode:
            logger.info('testing mode enabled!')
            self.irmode=False
        else:
            self.irmode=irmode
            if irmode: logger.info('infrared mode enabled!')

        self.stopped = True

    def run(self):
        logger.debug('started FrameMasker')
        while not self.stopped:
            if not self.q.empty():
                (frame, framename) = self.q.get() # retrieve frame from queue (First In Last Out)
                # frame = resize(frame, width=256)
                mask = get_hsv_mask(frame,irmode=self.irmode,testmode=self.testmode) # get hsv logical mask
                maskname = 'mask_'+framename
                try:
                    io.imsave('mask/'+maskname+'.jpg',mask) # save image to disk
                except Exception as e:
                    logger.error('failed to save image: '+'raw/raw_'+framename+'.jpg')
                    logger.error(e)
                    self.stop()
                    return
                logger.debug('{0} saved. {1} items left in queue.'.format(maskname,str(self.q.qsize())))
            else: logger.debug('Queue is empty, nothing to mask!')

    def start(self):
        self.stopped = False
        self.t = threading.Thread(target=self.run, args=(), name='masker')
        self.t.daemon = True
        self.t.start()

    def stop(self):
        logger.debug('masking remaining frames before stopping...')
        while(True):
            if self.q.empty():
                self.stopped = True
                self.t.join()
                logger.debug('stopped FrameMasker')
                break
def hsv2decimal(hsv):
    ''' Convert integer values to decimal percentages
        Hue [0 255]
        Saturation [0 100]
        Value [0 100]
    '''
    h=hsv[0]/255.0
    s=hsv[1]/100.0
    v=hsv[2]/100.0
    return [h,s,v]

def hsv_mask(img, limits):
    ''' Generate binary logical mask to filter RGB image to a range of HSV values (inclusive)
          inputs:
            img     as  PIL image object
            limits  as  tuple of two [Hue, Saturation, Value] lists or arrays
    '''
    hsv = color.rgb2hsv(img) # transform RGB to HLS
    lower_limit, upper_limit = hsv2decimal(limits[0]), hsv2decimal(limits[1])
    mask_3channel = np.zeros_like(hsv)
    for i in range(3):
        mask_3channel[:,:,i] = np.logical_and((hsv[:,:,i] >= lower_limit[i]),(hsv[:,:,i] <= upper_limit[i]))
    # mask = np.logical_and(np.logical_and(mask_3channel[:,:,0], mask_3channel[:,:,1]),mask_3channel[:,:,2]) # collapse to 2d array
    mask=mask_3channel
    return mask, mask_3channel

def get_hsv_mask(img,irmode=False,testmode=False):
    ''' Generate a binary logical mask to filter by a Hue-Saturation-Value range.
        Hue [0 255]
        Saturation [0 100]
        Value [0 100]
    '''
    if testmode:
        color_range = ([0,0,50], [100,50,100])
    elif irmode:
        color_range = ([0,0,0], [255,100,100])
    else:
        color_range = ([35, 50, 35], [120, 55, 100])
    mask, mask_3channel = hsv_mask(img, color_range)
    return mask

def stopAll(stream,reader,masker):
    reader.stop()
    stream.stop()
    masker.stop()
    return

def init(refresh=False):
    ''' Run hardware and software system checks.
    '''
    logger.debug('performing startup and system checks')
    try:
        # check for directory structure
        if os.path.exists('raw'):
            logger.debug('found directory: raw')
            if refresh:
                logger.debug('(refresh enabled: removing existing contents)')
                filelist = [ f for f in os.listdir('raw') ]
                for f in filelist:
                    try:
                        os.remove(os.path.join('raw', f))
                    except Exception as e:
                        logger.error(e)
                        return False
        else:
            os.mkdir('raw')
            logger.debug('created directory: raw')
    except:
        logger.critical('[NO GO] raw file directory')
        return False

    try:
        if os.path.exists('mask'):
            logger.debug('found directory: mask')
            if refresh:
                logger.debug('(refresh enabled: removing existing contents)')
                filelist = [ f for f in os.listdir('mask') ]
                for f in filelist:
                    try:
                        os.remove(os.path.join('mask', f))
                    except Exception as e:
                        logger.error(e)
                        return False
        else:
            os.mkdir('mask')
            logger.debug('created directory: mask')
    except:
        logger.critical('[NO GO] mask file directory')
        return False
    logger.info('[GO] file directories')

    try:
        # check video stream
        teststream = PiVideoStream(resolution=(640,480),framerate=60).start()
        logger.debug('(spooling PiVideoStream...)')
        time.sleep(2)
        testframe = teststream.read()
        teststream.stop()
    except:
        teststream.stop()
        logger.critical('[NO GO] PiVideoStream')
        return False
    logger.info('[GO] PiVideoStream')
    logger.debug('(restarting PiVideoStream...)')
    teststream.start()
    time.sleep(2)
    try:
        # check FrameReader
        testq=queue.Queue()
        testreader,testmasker = FrameReader(stream=teststream,q=testq,testmode=True), FrameMasker(stream=teststream,q=testq,testmode=True)
        logger.debug('(spooling FrameReader...)')
        testreader.start()
        time.sleep(1)
        testreader.stop()
    except:
        testreader.stop()
        logger.critical('[NO GO] FrameReader')
        return False
    logger.info('[GO] FrameReader')
    teststream.stop()

    try:
        # check FrameMasker
        logger.debug('(spooling FrameMasker...)')
        testmasker.start()
        time.sleep(1)
        testmasker.stop()
    except:
        logger.critical('[NO GO] FrameMasker')
        testmasker.stop()
        return False
    logger.info('[GO] FrameMasker')

    logger.info('All systems go!')
    return True

if __name__ == '__main__':
    # options
    parser = argparse.ArgumentParser()
    parser.add_argument('-q','--quiet',help='limited output to terminal, "INFO" items only',action='store_true')
    parser.add_argument('-r','--refresh',help='delete existing images before startup',action='store_true')
    parser.add_argument('-ir','--infrared',help='use alternate mask for PiCamera NoIR',action='store_true')
    args = parser.parse_args()

    LOG_FILE = os.path.splitext(__file__)[0]+'.log'

    if args.refresh:
        print('refresh mode enabled! clearing old log file before starting...')
        try:
            os.remove(LOG_FILE)
        except Exception as e:
            print(e)
            print('ERROR DELETING LOG FILE. ABORTING...')
            exit()

    # initialize logger
    logger= logging.getLogger(__name__)
    logFormatter = logging.Formatter('%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s')
    fileHandler = logging.FileHandler(LOG_FILE)
    fileHandler.setFormatter(logFormatter)
    logger.addHandler(fileHandler)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    if args.quiet:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.DEBUG)

    logger.info(' --- Where U At Plants? --- ')
    if not init(refresh=args.refresh):
        logger.critical('ABORTING STARTUP')
        exit()

    logger.debug('starting flight operations:')
    q = queue.Queue()
    resolution=(640,480) # http://picamera.readthedocs.io/en/release-1.10/fov.html
    framerate=60
    logger.debug('started threaded video stream ('+str(resolution)+','+str(framerate)+' fps)')
    stream = PiVideoStream(resolution=resolution,framerate=framerate).start()
    for i in reversed(range(1,4)):
        logger.debug('starting capture & processing in '+str(i)+' seconds')
        time.sleep(1)
    reader,masker=FrameReader(stream=stream,q=q),FrameMasker(stream=stream,q=q,irmode=args.infrared)
    reader.start()
    masker.start()

    print('Enter any character and press enter to stop the stream.')
    logger.info('Recording...')
    loopme=True
    while(loopme):
        try:
            user_input = input()
            if user_input:
                logger.critical('ABORTING')
                stopAll(stream,reader,masker)
                loopme=False
                break
        except:
            logger.critical('ABORTING')
            loopme=False
            stopAll(stream,reader,masker)
            break
