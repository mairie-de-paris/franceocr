import argparse
import cv2
import imutils
import logging
import math
import numpy as np

from operator import itemgetter

from skimage.filters import threshold_local, threshold_minimum
from skimage.exposure import adjust_sigmoid, equalize_adapthist
from skimage.restoration import denoise_bilateral
from imutils.perspective import four_point_transform

from franceocr.constants import DEBUG, IMAGE_HEIGHT
from franceocr.utils import DEBUG_display_image, INFO_display_image


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
    ratio = image.shape[0] / 650
    orig = image.copy()
    image = imutils.resize(image, height=650)

    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    edged = np.max(np.array([
        edge_detect(blurred[:, :, 0]),
        edge_detect(blurred[:, :, 1]),
        edge_detect(blurred[:, :, 2])
    ]), axis=0)
    mean = np.mean(edged)
    # Zero any value that is less than mean. This reduces a lot of noise.
    edged[edged <= mean] = 0

    DEBUG_display_image(image, "Image", alone=False)
    DEBUG_display_image(edged, "Edged")

    edged_8u = np.asarray(edged, np.uint8)

    # Find contours
    significant = find_significant_contours(edged_8u)

    contour = significant[0]
    # epsilon = 0.10 * cv2.arcLength(contour,True)
    # contour = cv2.approxPolyDP(contour, epsilon, True)
    contour = cv2.boxPoints(cv2.minAreaRect(contour))
    contour = np.int0(contour)

    if DEBUG:
        cv2.drawContours(image, [contour], -1, (255, 0, 0), 2)
        DEBUG_display_image(image, "Outline")

    # apply the four point transform to obtain a top-down
    # view of the original image
    warped = four_point_transform(orig, contour.reshape(4, 2) * ratio)

    INFO_display_image(orig, "Original", alone=False)
    INFO_display_image(warped, "Scanned")

    return warped


def improve_image(image):
    image = imutils.resize(image, height=650)

    # no_red_zones = image[:,:,2] <= 100
    # image[no_red_zones] = 255
    # image[~no_red_zones] = 0
    #
    # # To grayscale
    # image = np.amax(image, axis=2)
    # image = (image == 255) * 255
    # image = image.astype("uint8")

    # return image

    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 5))

    # smooth the image using a 3x3 Gaussian, then apply the blackhat
    # morphological operator to find dark regions on a light background
    image = cv2.GaussianBlur(image, (3, 3), 0)
    image = cv2.morphologyEx(image, cv2.MORPH_BLACKHAT, rectKernel)

    DEBUG_display_image(image, "Blackhat")

    # FIXME comment
    image = equalize_adapthist(image)
    image = adjust_sigmoid(image, cutoff=0.5, gain=7) * 255
    image = image.astype("uint8")
    image = cv2.bitwise_not(image)

    DEBUG_display_image(image, "Filter")

    # Courbe pour effacer les détails
    image[image <= 50] = 50
    image[image >= 220] = 220
    image = (image - 50) / 170 * 255
    image = image.astype("uint8")

    DEBUG_display_image(image, "Filter")

    # thresh = threshold_local(image, 35, offset=10)
    # # thresh = threshold_minimum(image)
    # image = image > thresh
    # image = image.astype("uint8") * 255
    #
    # cv2.imshow("Threshold", image)

    return image


def compute_skew(image):
    """Compute the skew of an image.

    Works by finding strong lines in the image and
    FIXME improve accuracy ?
    """
    image = imutils.resize(image, height=650)
    orig = image.copy()

    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    DEBUG_display_image(image, "Gray", alone=False)

    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    canny_threshold = 50
    edges = cv2.Canny(
        blurred,
        canny_threshold,
        canny_threshold * 3,
        apertureSize=3
    )

    DEBUG_display_image(edges, "Edges", alone=False)

    # FIXME remove useless
    # image = cv2.bitwise_not(image, image)
    # DEBUG_display_image(image, "BW", alone=False)

    rho_step = 1
    theta_step = np.pi / 180
    threshold = 100
    min_line_length = image.shape[1] * 0.6
    max_line_gap = 20
    lines = cv2.HoughLinesP(
        edges,
        rho_step,
        theta_step,
        threshold,
        minLineLength=min_line_length,
        maxLineGap=max_line_gap
    )

    image_angle = 0
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = math.atan2(y2 - y1, x2 - x1) / np.pi * 180
        logging.debug(angle)
        if abs(angle) < 15:
            cv2.line(orig, (x1, y1), (x2, y2), (255, 0, 0))
            image_angle += angle

    # Mean image angle in degrees
    image_angle /= len(lines)

    INFO_display_image(orig, "Lines")

    return angle


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

    INFO_display_image(rotated, "Rotated")

    return rotated


def remove_blur(image):
    """Remove blur on image.

    Too slow to be useful.
    """

    output = denoise_bilateral(
        imutils.resize(image, height=200),
        sigma_color=0.05,
        sigma_spatial=15
    )

    INFO_display_image(image, "Original", alone=False)
    INFO_display_image(output, "Deblurred")

    return output


def detect_text(image):
    """Find zones of the image where text is written.

    Not used in the pipeline.
    """
    # resize the image, and convert it to grayscale
    image = imutils.resize(image, height=650)
    if len(image.shape) == 3 and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # smooth the image using a 3x3 Gaussian, then apply the blackhat
    # morphological operator to find dark regions on a light background
    image = cv2.GaussianBlur(image, (3, 3), 0)
    blackhatKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 8))
    blackhat = cv2.morphologyEx(image, cv2.MORPH_BLACKHAT, blackhatKernel)

    cv2.imshow("Blackhat", blackhat)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    closingKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 7))
    thresh = cv2.morphologyEx(blackhat, cv2.MORPH_CLOSE, closingKernel)
    # thresh = cv2.erode(thresh, None, iterations=3)

    # closingKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 7))
    # thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, closingKernel)
    thresh = cv2.threshold(thresh, 127, 255, cv2.THRESH_BINARY)[1]

    cv2.imshow("Thresh", thresh)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    contours = cv2.findContours(
        thresh,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )[-2]
    print(contours)

    zones = []
    for contour in contours:
        contour = cv2.approxPolyDP(contour, 3, True)
        appRect = cv2.boundingRect(contour)
        x, y, w, h = appRect

        pX = 5
        pY = 5
        (x, y) = (x - pX, y - pY)
        (w, h) = (w + (pX * 2), h + (pY * 2))

        if w / h >= 3 and cv2.contourArea(contour) > 500:
            print(cv2.contourArea(contour))
            zones.append(appRect)
            cv2.rectangle(image, (x, y), (x + w, y + h), 0)

    cv2.imshow("Zones", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return zones
