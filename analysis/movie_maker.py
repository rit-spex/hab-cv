'''
Movie Maker 
Author:         Philip Linden
Date Created:   April 28, 2018
Description:
    Generate animated .gif from a series of frames. 
    Movie maker is specifically written to handle data 
    collected by Where U At Plants? (WUAP) and process
    them using OpenCV 3.3.x

    code structure inspired by 
		http://www.xavierdupre.fr/blog/2016-03-30_nojs.html
'''
import argparse
import numpy as np
import cv2
import os

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-i','--inputdirectory', type=str, help='Directory containing video frames as .jpg files')
	parser.add_argument('-o', '--outfile', type=str, help='Name of output video file')
	parser.add_argument('--fps', default=30.0, type=float,help='Output video framerate')
	parser.add_argument('--size', default=(640, 480), type=tuple, help='Output video')
	parser.add_argument('--flipRGB', help='RGB<-->BGR', action='store_true')
	# parser.add_argument('-p', '--preview', action='store_true',help='Display frames as video is encoded')
	args = parser.parse_args()

	fourcc = cv2.VideoWriter_fourcc(*'DIVX')  # use FourCC mpeg4 codec
	out = cv2.VideoWriter(args.outfile, fourcc, args.fps, args.size)

	frame_list = [f for f in os.listdir(args.inputdirectory)]
	print('found %s frames'%str(len(frame_list)))
	# format debug text
	font = cv2.FONT_HERSHEY_SIMPLEX
	bottomLeftCornerOfText = (10, 470)
	fontScale = 0.5
	fontColor = (0, 0, 255)
	lineType = 2

	print('encoding...')
	for counter, value in enumerate(frame_list):
		frame = cv2.imread(os.path.join(args.inputdirectory, value))
		if args.flipRGB:
			frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		font = cv2.FONT_HERSHEY_SIMPLEX
		cv2.putText(frame,'frame: ' + str(counter) + ' | ' + value,
                    bottomLeftCornerOfText,
                    font,
                    fontScale,
                    fontColor,
                    lineType)
		out.write(frame)
	
	print('done.')
