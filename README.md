# Where U At Plants? (WUAP): Capturing and Masking Images from Raspberry Pi 3 + Pi Camera
Where U At Plants? (WUAP) is a high-altitude balloon payload used to gather aerial image data for future vegetation density analysis. WUAP uses on-board image processing with a Raspberry Pi 3, Python 3 and OpenCV 3.3 to mask RGB images of the Earth and attempts to mask areas of high vegetation using colorspace transformations.

This project is the first of many SPEX experiments with on-board image processing and computer vision on high-altitude balloons and space systems.
Overarching goals and long-term visions for future work is outlined in the following Project Definition Document:  https://github.com/RIT-Space-Exploration/SPEX-Project-Definition-Documents/blob/master/HAB-CV/hab-cv.pdf

![WUAP Mission Patch](wuap.jpg)

## What does it do?
This script starts a video stream, samples "raw" video frames and saves them with single frame compression, and generates a binary mask according to an HSL color range and saves the mask corresponding to each video frame with single frame compression.

## That's it?
This project is driven by the objective to estimate vegetation density from imagery captured from a high altitude balloon.
The code and methods here describe only a portion of the development required for any sort of high-fidelity or real-time vegetation density mapping, but make up the basis for future work.

First and foremost, this project aims to _collect data_ in the form of as many images (visible and enar-infrared) of the Earth as possible.
More advanced analysis can be performed later on the ground, and more time can be spent developing and testing new algorithms for future flights.

While on-board processing is a secondary objective, we aim to demonstrate its usefulness with simple image processing algorithms performed in-flight.

# Research
Vegetation is identified two ways: Identification by color from visible-light images, and using the Normalized Vegetation Density Index from vilisble-light and near-infrared images.

## Identification by Color
(This is the image processing algorithm executed in-flight.)

## Normalized Vegetation Density Index
(This is an algorithm which will be used on future flights.)

See also: https://earthobservatory.nasa.gov/Features/MeasuringVegetation/measuring_vegetation_2.php

# Approach
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

# Using the Code

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

sudo pip3 install imutils

git clone https://github.com/RIT-Space-Exploration/hab-cv.git
cd hab-cv
mkdir raw
mkdir mask
```
For help installing OpenCV 3.3.x to a Raspberry Pi with Raspbian Stretch, consult [this great tutorial from PyImageSearch.com](https://www.pyimagesearch.com/2017/09/04/raspbian-stretch-install-opencv-3-python-on-your-raspberry-pi/).

## Running the Script
```
python3 hab_cv.py
```
Each raw video frame is saved in the `raw` folder.
Each corresponding mask is saved in the `mask` folder.

Press any key then Enter to close the video stream and stop all processes.
The masking process will mask the remaining frames in the queue before closing.
