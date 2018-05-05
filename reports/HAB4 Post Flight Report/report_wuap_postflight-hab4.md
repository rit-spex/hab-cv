# Where U At Plants (WUAP) Summary and Post-Flight Report
Philip Linden

May 2, 2018

## Abstract
[abstract goes here]

## Introduction
*Where U At Plants?* (WUAP) is a high-altitude balloon payload used to gather aerial image data for future vegetation density analysis.
WUAP uses on-board image processing with a Raspberry Pi 3, Python 3 and OpenCV 3.3 to mask RGB images of the Earth and attempts to mask areas of high vegetation using colorspace transformations.
This project is the first of many SPEX experiments with on-board image processing and computer vision on high-altitude balloons and space systems, whose objectives are to demonstrate these technologies to do science and push the limits of lightweight, low-cost hardware.

The science objective of mapping vegetation density is not driven by a particular scientist or research criteria.
Rather, it presents a straightforward problem and fertile testbed for developing a variety of key technologies and capabilities that the participants and contributors are interested in.
WUAP is as much of a technology demonstrator as it is a learning platform and engineering sandbox for student and alumni members of RIT Space Exploration to gain experience designing, integrating, and analyzing data from real-world systems.

## Objectives
The primary objective of WUAP was to collect a large dataset of ground-facing images from a Raspberry Pi Camera module paired with high altitude balloon sensor data.
A large dataset like this will enable future explorations of image processing components of future remote sensing experiments, including (but not limited to) deep learning techniques.
It is important to consider the specific camera being used, Raspberry Pi Camera module, as it is a low cost, easily integrated component. Rather than characterizing the sensor's performance in a laboratory setting, WUAP was intended to gather a "functional baseline."

A secondary objective was to demonstrate on-board processing during data collection. As part of the science goal to map vegetation density, a simple binary mask was generated using the RGB data to reject areas of the image that are not likely to be plants (i.e. not green in color).

The last objective of the mission was to provide the capability to determine a "ground truth" of vegetation density during post-flight processing using the method of Normalized Vegetation Density Index (NDVI).
NDVI is a method where the visible reflectance from plants (0.4-0.7 micron) and the near-infrared reflectance from plants (0.7-1.1 micron) are used to normalize an image, assuming healthy plants reflect much more visible light than infrared light.
By collecting near-infrared light for the same scene as the visible light images, the effectiveness on-board processing mask can be assessed and a confident baseline can be established.

## Payload Hardware

A contributing factor in the decision to use almost entirely commercial off-the-shelf (COTS) components is not only their cost, but also their simplicity to use and enormous amount of freely available documentation.
The WUAP payload concept and software was developed completely remotely from RIT Space Exploration Mission Control, where the payload components were assembled and integrated.
While COTS components made it easy to test the payload remotely by buying the same products, the physical separation between payload and HAB integration teams posed new challenges, and is partly responsible for some of the issues encountered during integration.


- raspberry pi
- cameras (vis only!)
- enclosure

## Payload Software
- software architecture
- masking algorithm

## Pre-Flight Testing
n/a lol

## Flight Profile

## Post-Flight Analysis
summary of notes in notebook

### What went right

### What went wrong

### What could have been done

## Future Work

## WUAP2
