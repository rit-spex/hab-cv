# Where U At Plants? (WUAP): Capturing and Masking Images from Raspberry Pi 3 + Pi Camera
Where U At Plants? (WUAP) is a high-altitude balloon payload used to gather aerial image data for future vegetation density analysis. WUAP uses on-board image processing with a Raspberry Pi 3, Python 3 and OpenCV 3.3 to mask RGB images of the Earth and attempts to mask areas of high vegetation using colorspace transformations.

This project is the first of many SPEX experiments with on-board image processing and computer vision on high-altitude balloons and space systems.

**Overarching goals and long-term visions for future work is outlined in the following Project Definition Document**:
https://github.com/RIT-Space-Exploration/SPEX-Project-Definition-Documents/blob/master/HAB-CV/hab-cv.pdf

![Example of HSL vegetation masking with HAB2 flight images](readme_assets/hsl_test2.gif)

## What does it do?
This script starts a video stream, samples "raw" video frames and saves them with single frame compression, and generates a binary mask according to an HSL color range and saves the mask corresponding to each video frame with single frame compression.

## That's it?
This project is driven by the objective to estimate vegetation density from imagery captured from a high altitude balloon.
The code and methods here describe only a portion of the development required for any sort of high-fidelity or real-time vegetation density mapping, but make up the basis for future work.

First and foremost, this project aims to _collect data_ in the form of as many images (visible and near-infrared) of the Earth as possible.
More advanced analysis can be performed later on the ground, and more time can be spent developing and testing new algorithms for future flights.

While on-board processing is a secondary objective, we aim to demonstrate its usefulness with simple image processing algorithms performed in-flight.

# Approach
On the main thread, values are initialized and 3 threads are opened to capture, process, and save image frames concurrently.
Data is passed between threads using a queue.

1. Using `PiVideoStream` from the [`imutils`](https://github.com/jrosebr1/imutils) library, a threaded video stream is opened to continuously capture frames from the camera module at the specified image size and framerate (640 x 480 @ 60 fps).

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

### Using OpenCV
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

### Using scikit-image
[`scikit-image`](http://scikit-image.org/) is a Python module with many handy image processing tools built upon NumPy and SciPy.
It is much easier to install on a Raspberry Pi, but is not as feature-complete as OpenCV.
```
sudo aptget update
sudo apt-get install python3-dev python3-pip
sudo pip3 install numpy scikit-image picamera
```
Since future flights are planned to use more advanced image processing and computer vision techniques, it is recommended to install OpenCV instead of scikit-image.
However, the primary objective of WUAP is to obtain a large collection of images for future CV experiments, so it may be more reliable to install scikit-image for this payload only.

## Running the Script
With OpenCV
```
python3 wuap.py
```
With scikit-image
```
python3 wuap_skimage.py
```

Each raw video frame is saved in the `raw` folder.
Each corresponding mask is saved in the `mask` folder.

Press any key then Enter to close the video stream and stop all processes.
The masking process will mask the remaining frames in the queue before closing.

# Basis for Experiment
Vegetation is identified two ways: Identification by color from visible-light images, and using the Normalized Vegetation Density Index from vilisble-light and near-infrared images.

## Identification by Color
_This is the image processing algorithm executed in-flight._

Plants are (mostly) green. Roads, buildings, and bodies of water (mostly) aren't.
This is the core principle for identifying vegetation from RGB aerial imagery.
While it is difficult to judge vegetation _density_ this way, it is fairly simple to identify vegetation from inorganic structures and generate a binary mask.

Thanks to chlorophyll and natural selection, plants come in a variety greenish colors.
To account for different brightnesses and a range of yellow-greens to blue-greens.
We can extend the acceptable range to some browns as well.
By changing our image colorspace from Red-Green-Blue (RGB) as captured by the picamera, to Hue-Lightness-Saturation (HLS) we can limit our mask's accepted _hue_ range while leaving _lightness_ and _saturation_ to allow wide ranges, thus allowing light blue greens to dark yellow greens all to register as vegetation.

For now, we visually tweak these ranges using [past flight video from HAB2](https://youtu.be/U40UZp3Z3a4?t=71), but in the future it is reasonable to assume another algoritm might be used for this calibration.
Not all plants are green, and not all green areas are vegetation. Despite this, initial testing demonstrates that a simple HSL masking of aerial imagery yields decent results.

![Example of HSL vegetation masking with Google Maps](readme_assets/hsl_test.gif)

An alternative to the HSL colorspace is Hue-Saturation-Value (HSV). 
HSV is similar to HSL in dividing the spectrum, but with less distict separation of black and white in the colorspace.
The [Wikipedia article on HSL and HSV](https://en.wikipedia.org/wiki/HSL_and_HSV) provides great insight into the construction of the two colorspaces and their distinctions.

HSV is used in the same way as HSL, the difference being the values of the color filter.
The primary benefit to using HSV over HSL is that many tools, such as scikit-image, have readily available RGB-to-HSV colorspace transformations, but not many have RGB-to-HSL transformations.

## Normalized Vegetation Density Index (NDVI)
_This is an algorithm which will be used on future flights._

A more precise method of measuring vegetation density is through spectroscopy.
To the naked eye, we see the reflected wavelengths of green that chlorophyll in vegetation reflects.
However, plants respond quite strikingly in the infrared portion of the spectrum as well.

> The pigment in plant leaves, chlorophyll, strongly absorbs visible light (from 0.4 to 0.7 µm) for use in photosynthesis. The cell structure of the leaves, on the other hand, strongly reflects near-infrared light (from 0.7 to 1.1 µm). The more leaves a plant has, the more these wavelengths of light are affected, respectively. [[1]](https://earthobservatory.nasa.gov/Features/MeasuringVegetation/measuring_vegetation_2.php)

A well-established method of measuring vegetation density has arisen from this facet of nature called the Normalized Vegetation Density Index (NDVI).
NDVI normalizes the infrared response of regions on the earth to their response in the visible range.
This effectively transforms the imaged region to show areas where visible light is strongly absorbed and infrared light is strongly reflected.

```
Let
    NIR = near-infrared wavelength response (0.7-1.1 micron)
    VIS = visible wavelength response (0.4-0.7 micron)

Such that
    NDVI = (NIR - VIS)/(NIR + VIS)
```

NDVI is effective in rejecting man-made structures, water, and land features since these types of regions rarely strongly absorb visible AND strongly reflect infrared (usually its one or the other, not both).

![Multispectral raspberry pi: first light (NDVI images)](https://publiclab.org/system/images/photos/000/009/861/original/Screen_Shot_2015-05-10_at_17.30.58.png)
> Public Lab demonstrates how applying a clever colormap to NDVI data makes identifying vegetation very clear against the background. [[2]](https://publiclab.org/notes/khufkens/05-10-2015/multispectral-raspberry-pi-first-light-ndvi-images)

- [1] https://earthobservatory.nasa.gov/Features/MeasuringVegetation/measuring_vegetation_2.php
- [2] https://publiclab.org/notes/khufkens/05-10-2015/multispectral-raspberry-pi-first-light-ndvi-images

![WUAP Mission Patch](readme_assets/wuap.jpg)
