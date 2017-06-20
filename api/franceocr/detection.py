import cv2
import imutils
import numpy as np

from franceocr.config import IMAGE_HEIGHT


def is_blurred(image, threshold=100):
    """
    Detect if image is blurred

    FIXME Doesn't work
    """
    # All images should have the same amout of pixels
    ratio = float(2E6) / float(image.shape[0] * image.shape[1])
    image = cv2.resize(image, (0, 0), fx=ratio, fy=ratio)

    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blur_map = cv2.Laplacian(image, cv2.CV_64F)
    score = np.var(blur_map)

    print(score)

    return score < threshold


def is_extracted(image):
    """Detect if document is already (almost) extracted"""
    return False
