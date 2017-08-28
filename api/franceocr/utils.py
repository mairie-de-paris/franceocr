import cv2
import imutils
import numpy as np

from franceocr.config import DEBUG, INFO


def display_image(image, window_name="Image", alone=True, resize=400):
    if resize is not False:
        image = imutils.resize(image, height=resize)

    cv2.imshow(window_name, image)

    if alone:
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def DEBUG_display_image(image, window_name="Image", alone=True, resize=400):
    if DEBUG or INFO:
        display_image(image, window_name, alone, resize)


def INFO_display_image(image, window_name="Image", alone=True, resize=400):
    if INFO:
        display_image(image, window_name, alone, resize)


def in_bounds(bbox, image):
    """ Cut bbox to fit in the image """
    bbox[:, 0] = np.maximum(0, np.minimum(bbox[:, 0], image.shape[1]))
    bbox[:, 1] = np.maximum(0, np.minimum(bbox[:, 1], image.shape[0]))

    return bbox
