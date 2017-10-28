## https://www.pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/

from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import cv2
import datetime

class FPS:
	def __init__(self):
		self._start = None
		self._end = None
		self._numFrames = 0

	def start(self):
		self._start = datetime.datetime.now()
		return self

	def stop(self):
		self._end = datetime.datetime.now()

	def update(self):
		self._numFrames += 1

	def elapsed(self):
		return (self._end - self._start).total_seconds()

	def fps(self):
		try: fps= self._numFrames / self.elapsed()
		except: fps=1000000
		return fps

class PiVideoStream:
	def __init__(self, resolution=(800, 640), framerate=60):
		self.camera = PiCamera()
		self.camera.resolution = resolution
		self.camera.framerate = framerate
		self.rawCapture = PiRGBArray(self.camera, size=resolution)
		self.stream = self.camera.capture_continuous(self.rawCapture,
			format="bgr", use_video_port=True)
		self.frame = None
		self.stopped = False

	def start(self):
		Thread(target=self.update, args=()).start()
		return self

	def update(self):
		for f in self.stream:
			self.frame = f.array
			self.rawCapture.truncate(0)
			if self.stopped:
				self.stream.close()
				self.rawCapture.close()
				self.camera.close()
				return

	def read(self):
		return self.frame

	def stop(self):
		self.stopped = True


def hsl_mask(img, limits):
    hls = cv2.cvtColor(img, cv2.COLOR_BGR2HLS_FULL)
    lower_limit, upper_limit = np.array(limits[0], dtype='uint8'), np.array(limits[1], dtype='uint8')
    mask = cv2.inRange(hls, lower_limit, upper_limit)
    masked_img = cv2.bitwise_and(img, img, mask=mask)
    return mask, masked_img

colors=([35, 5, 35], [120, 140, 255])
vs = PiVideoStream().start()
while(True):
	fps = FPS().start()
	frame = vs.read()
	# mask, masked_img = hsl_mask(frame,colors)

	fps.update()
	fps.stop()
	# cv2.imshow('window', frame)
	print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
	if cv2.waitKey(25) & 0xFF == ord('q'):
		cv2.destroyAllWindows()
		break

cv2.destroyAllWindows()
vs.stop()
