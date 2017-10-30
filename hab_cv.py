from __future__ import print_function
from imutils.video.pivideostream import PiVideoStream
from imutils.convenience import resize
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import datetime
import time
import cv2
import numpy as np
import threading
import queue
import logging

class FrameReader():
    def __init__(self):
        super(FrameReader,self).__init__()
        self.stopped = True

    def run(self):
        while not self.stopped:
            if not q.full():
                frame=stream.read()
                framename=datetime.datetime.now().time().strftime("%Y%m%d-%H%M%S")
                cv2.imwrite('raw/'+framename+'.jpg',frame)
                q.put((frame,framename))
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

class FrameMasker(threading.Thread):
    def __init__(self):
        super(FrameMasker,self).__init__()
        self.stopped = True

    def run(self):
        logging.debug('started FrameMasker')
        while not self.stopped:
            if not q.empty():
                (frame, framename) = q.get()
                frame = resize(frame, width=300)
                mask = get_hsl_mask(frame)
                cv2.imwrite('mask/'+framename+'.jpg',mask)
            else: logging.debug('Queue is empty!')

    def start(self):
        self.stopped = False
        t = threading.Thread(target=self.run, args=(), name='masker')
        t.daemon = True
        t.start()

    def stop(self):
        self.stopped = True
        logging.debug('stopped FrameMasker')

def hsl_mask(img, limits):
    hls = cv2.cvtColor(img, cv2.COLOR_BGR2HLS_FULL)
    lower_limit, upper_limit = np.array(limits[0], dtype='uint8'), np.array(limits[1], dtype='uint8')
    mask = cv2.inRange(hls, lower_limit, upper_limit)
    return mask

def get_hsl_mask(img, selection='vegetation'):
    # LIMITS IN HLS - Hue, Lightness, Saturation
    # range: 0 to 255
    # SEE: color_previewer()
    ranges = {'vegetation': ([35, 5, 35], [120, 140, 255]),
              'water': ([120, 35, 20], [180, 175, 255]),
              'urban': ([0, 0, 0], [255, 255, 20])
              }
    mask = hsl_mask(img, ranges[selection])
    return mask

# def ndvi(img_color, img_nir):
#     nir = cv2.cvtColor(img_nir, cv2.COLOR_RGB2GRAY)
#     r, g, b = cv2.split(img_color)
#
#     num = nir.astype(float) - r.astype(float)
#     den = nir.astype(float) + r.astype(float)
#     den[den == 0] = np.finfo(float).eps  # very small number instead of zero
#
#     return np.divide(num, den)

def stopAll(stream,reader,masker):
    reader.stop()
    masker.stop()
    stream.stop()
    return

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='(%(threadName)-9s) %(message)s',)

    q = queue.Queue()
    resolution=(640,480) # http://picamera.readthedocs.io/en/release-1.10/fov.html
    framerate=60
    logging.debug('started threaded video stream ('+str(resolution)+','+str(framerate)+' fps)')
    stream = PiVideoStream(resolution=resolution,framerate=framerate).start()
    for i in reversed(range(1,6)):
        logging.debug('starting capture & processing in '+str(i)+' seconds')
        time.sleep(1)
    reader,masker=FrameReader(),FrameMasker()
    reader.start()
    masker.start()

    time.sleep(10)
    stopAll(stream,reader,masker)
