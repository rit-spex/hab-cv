## https://www.pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/

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

def hsl_mask(img, limits):
	hls = cv2.cvtColor(img, cv2.COLOR_BGR2HLS_FULL)
	lower_limit, upper_limit = np.array(limits[0], dtype='uint8'), np.array(limits[1], dtype='uint8')
	mask = cv2.inRange(hls, lower_limit, upper_limit)
	masked_img = cv2.bitwise_and(img, img, mask=mask)
	return mask, masked_img

colors=([35, 5, 35], [120, 140, 255])

print("[INFO] started threaded video stream")
vs = PiVideoStream(framerate=60).start()
time.sleep(2.0)
fps = FPS()
fps.start()
while fps._numFrames < 500:
	frame = vs.read()
	# frame = imutils.resize(frame, width=400)
	mask, masked_img = hsl_mask(frame,colors)
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
