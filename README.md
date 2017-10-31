# Capturing and Masking Images from Raspberry Pi 3 + Pi Camera
This script starts a video stream, samples "raw" video frames and saves them with single frame compression, and generates a binary mask according to an HSL color range and saves the mask corresponding to each video frame with single frame compression.

## Requirements & Dependencies
Raspberry Pi 3 Model B + Raspbian Stretch Lite (OS)
Raspberry Pi Camera Module v2 (or Pi Camera NoIR v2)

```
sudo apt-get update
sudo apt-get install cmake build-essential pkg-config
sudo apt-get install libgtk2.0-dev libtbb-dev
sudo apt-get install libjasper-dev libjpeg-dev libpng-dev libtiff-dev
sudo apt-get install libavcodec-dev libavutil-dev libavformat-dev libswscale-dev
sudo apt-get install libdc1394-22-dev libv4l-dev

sudo apt-get install python-dev python3-dev python-numpy python-scipy
sudo apt-get install libopencv-dev python-opencv
sudo pip3 install "picamera[array]"

sudp pip3 install imutils
```

## Approach
On the main thread, values are initialized and 3 threads are opened to capture, process, and save image frames concurrently.
Data is passed between threads using a queue.

1. Using `PiVideoStream` from the `imutils` library, a threaded video stream is opened to continuously capture frames from the camera module at the specified image size and framerate (640 x 480 @ 60 fps).

2. A thread is opened to read and save frames from the video stream as fast as possible.
Each iteration of the looped read process, the most recent frame of the continuous stream (Thread 1) is sampled and saved as a JPEG image.
The frame (a 640 x 480 x 3 numpy array) and its label (`time.time()` as a formatted string) are pushed to a queue as a tuple.

3. A thread is opened to pop frames from the queue, apply a color mask and save that mask as fast as possible.
Each iteration of the looped mask process, the first tuple of the FIFO queue (frame array and its name) is popped from the queue. 
The frame colorspace is converted to hue-saturation-lightness (HSL) and a pixel-wise binary mask is generated.
Any pixel within the given tunable HSL value range is given a value of 1, all other pixels are given a value of 0.
The binary mask is saved as a JPEG image.
(To improve speed, the frame may be resized. However, in testing the `resize -> mask -> save` process was the same speed or slower than a full-frame `mask -> save` process.)

In desktop testing, the all threads run continuously until the user provides input.
After user input is given, the video stream and read processes are stopped.
The mask process finishes working on the remaining frames in the queue then is stopped.

In flight, all threads run continuously until the system runs out of power or memory is full.
If either of these conditions are reached, the script obviously is halted and does not gracefully exit but all frames until that point would have been saved - but the masking thread will likely be hopelessly behind the capture thread in terms of processing.

## Running the Script
```
git clone https://github.com/RIT-Space-Exploration/hab-cv.git
cd hab-cv
mkdir raw
mkdir mask
python3 hab_cv.py
```
Each raw video frame is saved in the `raw` folder. 
Each corresponding mask is saved in the `mask` folder.

Press any key then Enter to close the video stream and stop all processes.
The masking process will mask the remaining frames in the queue before closing.
