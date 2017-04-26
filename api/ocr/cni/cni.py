import argparse
import cv2
import imutils
import math
import numpy as np

from skimage.filters import threshold_local, threshold_otsu
from skimage.morphology import *
from skimage.restoration import denoise_bilateral
from transform import four_point_transform

if __name__ == "__main__":
    image = cv2.imread("../../static/img/louis2.jpg")
