from __future__ import print_function
from imutils.video.pivideostream import PiVideoStream
from imutils.video import FPS
from picamera.array import PiRGBArray
from picamera import PiCamera
import numpy as np
import imutils
import time
import cv2
import numpy

def smooth(img, radius, kind='open'):
    kernel = np.ones((radius, radius), np.uint8)
    if kind == 'gaussian':
        img = cv2.GaussianBlur(img, (radius, radius), 0)
    elif kind == 'open':
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    elif kind == 'close':
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    elif kind == 'erode':
        img = cv2.erode(mask, kernel, iterations=1)
    elif kind == 'dilate':
        img = cv2.dilate(mask, kernel, iterations=1)
    return img

def hsl_mask(img, limits, radius=1):
    hls = cv2.cvtColor(img, cv2.COLOR_BGR2HLS_FULL)
    lower_limit, upper_limit = np.array(limits[0], dtype='uint8'), np.array(limits[1], dtype='uint8')
    mask = cv2.inRange(hls, lower_limit, upper_limit)
    if radius >1: mask = smooth(mask, radius, kind='close')
    masked_img = cv2.bitwise_and(img, img, mask=mask)
    return mask, masked_img

def get_hsl_mask(img, selection='vegetation', smoothing=0):
    # LIMITS IN HLS - Hue, Lightness, Saturation
    # range: 0 to 255
    # SEE: color_previewer()
    ranges = {'vegetation': ([35, 5, 35], [120, 140, 255]),
              'water': ([120, 35, 20], [180, 175, 255]),
              'urban': ([0, 0, 0], [255, 255, 20])
              }
    mask, masked_img = hsl_mask(img, ranges[selection], smoothing)
    return mask, masked_img

# def ndvi(img_color, img_nir):
#     nir = cv2.cvtColor(img_nir, cv2.COLOR_RGB2GRAY)
#     r, g, b = cv2.split(img_color)
#
#     num = nir.astype(float) - r.astype(float)
#     den = nir.astype(float) + r.astype(float)
#     den[den == 0] = np.finfo(float).eps  # very small number instead of zero
#
#     return np.divide(num, den)

print("[INFO] started threaded video stream")
vs = PiVideoStream(framerate=60).start()
time.sleep(2.0)
fps = FPS()
fps.start()
while fps._numFrames < 500:
	frame = vs.read()
	# frame = imutils.resize(frame, width=400)
	mask, masked_img = get_hsl_mask(frame)
	# cv2.imshow('', masked_img)
	# if cv2.waitKey(25) & 0xFF == ord('q'):
	# 	cv2.destroyAllWindows()
	# 	break
	fps.update()

fps.stop()
print("[INFO] frames sampled: {}".format(str(fps._numFrames)))
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] avg. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
