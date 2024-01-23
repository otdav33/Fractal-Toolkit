import argparse
from PIL import Image
import os
import cv2
import numpy as np

parser = argparse.ArgumentParser(prog='assemble animation from still images', description='assemble animation from still images')
parser.add_argument('directory',
    help='Should contain only files of the format animationname_framenumber_etc.whatever',
    nargs=1)
parser.add_argument('outfile',
    help='Output file destination',
    nargs=1)

args = parser.parse_args()
directory = args.directory[0]
outfile = args.outfile[0]

listings = os.listdir(directory)
framefiles = [''] * len(listings)
for filename in listings:
    framenum = int(filename.split('_')[1])
    framefiles[framenum] = filename

video = cv2.VideoWriter(outfile, cv2.VideoWriter_fourcc(*'XVID'), 60, (1920, 1080))
for f in framefiles:
    image = Image.open(directory + '/' + f)
    opencv_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    video.write(opencv_img)
