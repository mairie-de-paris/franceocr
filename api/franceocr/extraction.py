import argparse
import cv2
import imutils
import logging
import math
import numpy as np

from operator import itemgetter

from skimage.filters import threshold_local
from skimage.exposure import adjust_sigmoid, equalize_adapthist, equalize_hist
from skimage.morphology import binary_closing, closing
from skimage.restoration import denoise_bilateral
from imutils.perspective import four_point_transform

from franceocr.config import DEBUG, IMAGE_HEIGHT
from franceocr.utils import DEBUG_display_image, DEBUG_print, INFO_display_image


def edge_detect(channel):
    sobelX = cv2.Sobel(channel, cv2.CV_16S, 1, 0)
    sobelY = cv2.Sobel(channel, cv2.CV_16S, 0, 1)
    sobel = np.hypot(sobelX, sobelY)

    return sobel


def find_significant_contours(edged_image, ratio=0.05):
    """Find contours big enough.

    The image must have strong edges for the function to work properly.
    """
    # Find contours
    contours = cv2.findContours(
        edged_image,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )[-2]

    # Sort by area
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # Prune small contours
    tooSmall = edged_image.size * ratio
    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if area <= tooSmall:
            contours = contours[:i]
            break

    return contours


def extract_document(image):
    orig = image.copy()
    ratio = image.shape[0] / IMAGE_HEIGHT

    image = imutils.resize(image, height=IMAGE_HEIGHT)

    # === Beginning of the first pass of the extraction === #

    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([210 / 2, 60, 50])
    upper_blue = np.array([230 / 2, 255, 255])
    image_blue = cv2.inRange(image_hsv, lower_blue, upper_blue)

    blurred = cv2.GaussianBlur(image_blue, (3, 3), 0)

    DEBUG_display_image(image, "Image", alone=False)
    DEBUG_display_image(blurred, "Edged")

    # Find contours
    significant = find_significant_contours(blurred, ratio=0.01)

    contour = significant[0]
    contour = cv2.boxPoints(cv2.minAreaRect(contour))

    # FIXME Buffer overflow
    HEADER_TO_BODY = 1400 / 125
    contour[0] = contour[1] + HEADER_TO_BODY * (contour[0] - contour[1])
    contour[3] = contour[2] + HEADER_TO_BODY * (contour[3] - contour[2])
    contour = np.int0(contour)

    image = four_point_transform(image, contour.reshape(4, 2))
    output = four_point_transform(orig, contour.reshape(4, 2) * ratio)

    DEBUG_display_image(image, "Extracted")

    # === End of the first pass of the extraction === #
    # === Deskewing === #

    # FIXME pertinent ?
    angle = compute_skew(image)
    image = deskew_image(image, angle)
    output = deskew_image(output, angle)

    # === End of deskewing === #
    # === Beginning of the second pass of the extraction === #
    # ==== Remove additionnal space below the document ==== #

    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edged = edge_detect(image)
    edged = np.asarray(edged, np.uint8)

    totals = np.sum(edged, axis=1)
    totals_threshold = 0.7 * np.max(totals)
    totals[totals <= totals_threshold] = 0

    # First line from the 9/10s
    yMin = int(edged.shape[0] * 9 / 10)
    for y0 in range(yMin, edged.shape[0]):
        if totals[y0]:
            break

    # Safeguard: don't cut the image if not necessary
    if y0 == yMin:
        y0 = edged.shape[0]

    cv2.line(edged, (0, y0), (1000, y0), (255, 255, 255), 3)

    DEBUG_display_image(edged, "Image")

    output = output[:int(y0 * ratio), :]

    # === End of the second pass of the extraction === #

    INFO_display_image(orig, "Original", alone=False)
    INFO_display_image(output, "Scanned")

    return output


def improve_image(image):
    image = imutils.resize(image, height=IMAGE_HEIGHT)

    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.GaussianBlur(image, (5, 5), 0)

    # smooth the image using a 3x3 Gaussian, then apply the blackhat
    # morphological operator to find dark regions on a light background
    rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 40))
    image = cv2.morphologyEx(image, cv2.MORPH_BLACKHAT, rectKernel)
    image = cv2.bitwise_not(image)

    DEBUG_display_image(image, "Blackhat")

    # FIXME comment
    image = equalize_hist(image)
    image = (image * 255).astype("uint8")

    DEBUG_display_image(image, "Filter1")

    # Courbe pour effacer les détails
    min_level = 10
    max_level = 30
    image[image <= min_level] = min_level
    image[image >= max_level] = max_level
    image = (image - min_level) / (max_level - min_level) * 255
    image = image.astype("uint8")

    DEBUG_display_image(image, "Filter2")

    # Remove pepper
    image = closing(image)

    INFO_display_image(image, "Threshold")

    return image


def compute_skew(image):
    """Compute the skew of an image.

    Works by finding strong lines in the image and
    FIXME improve accuracy ?
    """
    image = imutils.resize(image, height=IMAGE_HEIGHT)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    DEBUG_display_image(image, "Gray", alone=False)

    blurred = cv2.GaussianBlur(image, (3, 3), 0)
    canny_threshold = 50
    edged = cv2.Canny(
        blurred,
        canny_threshold,
        canny_threshold * 3,
        apertureSize=3
    )

    DEBUG_display_image(edged, "Edges", alone=False)

    # FIXME remove useless
    # image = cv2.bitwise_not(image, image)
    # DEBUG_display_image(image, "BW", alone=False)

    rho_step = 1
    theta_step = 1 * np.pi / 180
    threshold = 100
    min_line_length = image.shape[1] * 0.6
    max_line_gap = 40
    lines = cv2.HoughLinesP(
        edged[220:, :],
        rho_step,
        theta_step,
        threshold,
        minLineLength=min_line_length,
        maxLineGap=max_line_gap
    )

    image_angle = 0
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = math.atan2(y2 - y1, x2 - x1) / np.pi * 180
            logging.debug(angle)
            if abs(angle) < 15:
                cv2.line(image, (x1, y1), (x2, y2), (255, 0, 0))
                image_angle += angle

        # Mean image angle in degrees
        image_angle /= len(lines)

    DEBUG_print("Document angle: {}".format(image_angle))
    DEBUG_display_image(image, "Lines")

    return image_angle


def deskew_image(image, angle):
    """Remove skew from a image, given the right rotation angle.

    """
    rot_mat = cv2.getRotationMatrix2D(
        (image.shape[0] / 2, image.shape[1] / 2),
        angle,
        1
    )

    height = image.shape[0]
    width = image.shape[1]
    rotated = cv2.warpAffine(
        image,
        rot_mat,
        (width, height),
        flags=cv2.INTER_CUBIC
    )

    DEBUG_display_image(rotated, "Rotated")

    return rotated
