# HAB-CV - Plant Life Automatic NDVI with Telemetry from a High Altitude Balloon (PLANTHAB)
Philip Linden
July 31, 2018

## WUAP2 Objectives and Intent
The initial flight of Where U At Plants? (WUAP) on HAB4 did not meet all of its objectives or design goals and encountered unexpected problems in flight.[[1]](https://github.com/RIT-Space-Exploration/hab-cv/blob/master/reports/HAB4%20Post%20Flight%20Report/report_wuap_postflight-hab4.md) 
A follow-on payload, PLANTHAB, will attempt the same mission as WUAP but will place more emphasis and effort on testing, reliability, and system architecture. 

PLANTHAB Priorities
1. **Understanding of the system.** There should be no surprises in flight, and if goals or target performanceare not met it should be known by how much.
2. **Reliability and stability.** The system should behave the same way every time, and should produce the same output for a given (known) set of inputs.
3. **Performance.** The quality of output data should reach the maximum possible for the system's capability. Realize all the potential of the system.

WUAP demonstrated the core concepts of image processing and imaging payloads on high altitude balloon missions[[2]](https://github.com/RIT-Space-Exploration/hab-cv/blob/master/reports/Project%20Definition%20Document/hab-cv.pdf) but was severely lacking in pre-flight testing, system architecture development, and quality of results, leaving much to be desired. 

PLANTHAB seeks to achieve the same objectives as WUAP: conduct VNIR (visible and near-infrared) aerial imaging and perform on-board image processing with the intent to map vegetation density using low-cost consumer electronics.
However, PLANTHAB is held to a higher standard than WUAP in terms of the expectation of effort, execution, and quality of results, as outlined above.

## Unanswered Questions
- [Imaging] WHat is the spectral response of the Pi Camera V2? The Pi Camera V2 NoIR?
- [Imaging] What is the spatial resolution (GSD) of images at 480p? 1080p? How does it vary with altitude?
- [Imaging] What is the lens distortion for the Pi Camera V2 standard lens?
- [Imaging] Given the spectral response of the cameras, is NDVI possible without filters? With filters?
- [Imaging/Image Processing/Mechanical] How precisely do the cameras need to be aligned? How do we align them? Do we align with hardware, software, or both?
- [Imaging/Embedded Systems] What is the best way to control/command the cameras capture timing?
- [Image Processing] What framerate is optimal for processing? For image quality? Where's the pareto frontier for framerate/resolution combinations vs processing?
- [Image Processing] How can image saving and processing operations be more efficient? More reliable?
- [Image Processing/Computer Vision] How much processing is reasonable to do in flight? How complex? Where's the pareto frontier for usefulness/complexity of operations vs processing capability?
- [Image Processing/Computer Vision] Can images be preprocessed in flight to make analysis/development on the ground easier?
- [Image Processing/Computer Vision/System Integration] Can auxiliary data (other sensor data) be combined with image data for useful for Computer Vision algorithms? Which metrics are needed?
- [Computer Vision] How can vegetated areas and vegetation density be estimated from visible RGB images?
- [Computer Vision/Imaging] What is the minimum pixel resolution where useful CV can be done? Max altitude?
- [Computer Vision] Can a vegetation density mapping model trained on NASA datasets be applied to HAB aerial images?
- [Computer Vision] Can roads and buildings be identified from HAB aerial images? Can this be done in flight?
- [Computer Vision] Is VNIR imaging (with Pi Camera NoIR, for example) useful on its own or is Visible RGB better for vegetation mapping? Are both required?
- [Embedded Systems] What is the minimum power needed for payload electronics to operate reliably under load?
- [Embedded Systems] How does the performance of single-board-computers, camera modules, and other electronics under load change with time? Temperature? Pressure? Power? Used storage space?
- [Embedded Systems/System Architecture] What is the most precise and reliable method of synchronizing image captures from multiple cameras?
- [Mechanical] What are the thermal characteristics of the payload electronics under load? Do they overheat in open air? In an insulated enclosure?
- [Mechanical] What is the best enclosure design for thermal stability/management? For vibrations? For alignment?
- [Image Processing/Embedded Systems/Software/Test] How can software be tested for functionality on development hardware? Flight hardware?
- [Image Processing/Embedded Systems/Software/Test] How can software be tested for benchmarking (power, reliability, performance over time)?
- [Image Processing/Embedded Systems/Software/Test] How can software be monitored during testing? Pre-flight? In-flight?
- [Image Processing/Embedded Systems/Software/Test] How can software be tuned or calibrated?

## Example Tasks
- [Imaging] Measure camera module average pixel response vs wavelength, targeting 400nm-1100nm.
- [Imaging] Calculate spatial resolution (GSD) from pixel density, field of view, and altitude.
- [Imaging] Measure lens distortion by imaging a standard target and generate a distortion correction map.
- [Computer Vision] Develop NDVI and vegetation density estimation algorithms using NASA aerial photography (Visible and VNIR), and use NASA NDVI/EVI data as ground truth.
- [Computer Vision] Investigate the effectiveness of these algorithms at very low resolution images, and determine the minimum viable resolution.
- [Imaging/Image Processing/Mechanical] Develop the most efficient architecture for reliably differencing images from two cameras, including calibration, hardware alignment or mounting, and software alignment techniques.
- [Image Processing/Software] Develop reliable software for retrieving, saving and processing images.
- [Software] Develop dev tools for debugging, monitoring, benchmarking, and tuning payload systems.
- [Embedded Systems] Design a system architecture that reliably and efficiently captures synchronized images.
    - Example architecture 1: 2 SBCs, 1 camera each (like WUAP) - SBCs independently capture frames based on a master trigger/clock.
    - Example architecture 2: 1 SBC, 2 cameras - Command 2 camera modules from a single SBC, "outsource" processing to a second SBC if needed.
    - Example architecture 3: 1 SBC, 1+ auxiliary boards - Use an SBC to handle images and processing but "outsource" timing and frame captures to a specialized daughter board for each camera.

## References
[1] Linden, Philip. "[Where U At Plants (WUAP) Technical Report](https://github.com/RIT-Space-Exploration/hab-cv/blob/master/reports/HAB4%20Post%20Flight%20Report/report_wuap_postflight-hab4.md)," 2018.

[2] Linden, P., Maggio, J., Tarazevits, T.J. "[On-Board Image Processing and Computer Vision Techniques on Low-Cost Consumer Electronics for Vegetaiton Density Mapping and Other Experiments](https://github.com/RIT-Space-Exploration/hab-cv/blob/master/reports/Project%20Definition%20Document/hab-cv.pdf)," 2017.
