import cv2
import imutils
import logging
import math
import numpy as np

from skimage.exposure import equalize_hist
from skimage.morphology import closing
from imutils.perspective import four_point_transform, order_points

from franceocr.config import IMAGE_HEIGHT
from franceocr.utils import (
    DEBUG_display_image,
    INFO_display_image,
    in_bounds
)


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

    # === Beginning of the pass 0 of the extraction === #
    # Use edges to find a first approximation of the document

    blurred = cv2.GaussianBlur(image, (3, 3), 0)
    edged = np.max(np.array([
        edge_detect(blurred[:, :, 0]),
        edge_detect(blurred[:, :, 1]),
        edge_detect(blurred[:, :, 2])
    ]), axis=0)
    mean = np.mean(edged)
    # Zero any value that is less than mean. This reduces a lot of noise.
    edged[edged <= 1.5 * mean] = 0

    edged_8u = np.asarray(edged, np.uint8)

    DEBUG_display_image(edged_8u, "Edged")

    # Find contours
    significant = find_significant_contours(edged_8u)

    contour = significant[0]
    bbox = cv2.boxPoints(cv2.minAreaRect(contour))
    bbox = np.int0(bbox)

    image = four_point_transform(image, bbox.reshape(4, 2))
    orig = four_point_transform(orig, bbox.reshape(4, 2) * ratio)

    DEBUG_display_image(image, "Extracted0")

    # === End of the pass 0 of the extraction === #
    # === Beginning of the first pass of the extraction === #
    # Finds the blue header of the CNI to improve the extraction

    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([210 / 2, 120, 50])
    upper_blue = np.array([230 / 2, 255, 255])
    image_blue = cv2.inRange(image_hsv, lower_blue, upper_blue)

    blurred = cv2.GaussianBlur(image_blue, (5, 5), 0)

    DEBUG_display_image(image, "Image", alone=False)
    DEBUG_display_image(blurred, "Blue component", alone=False)

    # Find contours
    significant = find_significant_contours(blurred, ratio=0.01)

    contour = significant[0]
    bbox = cv2.boxPoints(cv2.minAreaRect(contour))

    # Make sure the document has the right orientation
    center_x, center_y = np.mean(bbox, axis=0)

    if center_x < image.shape[1] / 3:
        image = imutils.rotate_bound(image, 90)
        orig = imutils.rotate_bound(orig, 90)
        # Rotate bbox 90°
        tmp = bbox[:, 0].copy()
        bbox[:, 0] = image.shape[1] - bbox[:, 1]
        bbox[:, 1] = tmp

    elif center_x > 2 * image.shape[1] / 3:
        image = imutils.rotate_bound(image, -90)
        orig = imutils.rotate_bound(orig, -90)
        # Rotate bbox -90°
        tmp = bbox[:, 0].copy()
        bbox[:, 0] = bbox[:, 1]
        bbox[:, 1] = image.shape[0] - tmp

    elif center_y > 2 * image.shape[0] / 3:
        image = imutils.rotate_bound(image, 180)
        orig = imutils.rotate_bound(orig, 180)
        # Rotate bbox 180°
        bbox = (image.shape[1], image.shape[0]) - bbox

    bbox = order_points(bbox)

    HEADER_TO_BODY = 1460 / 125
    bbox[2] = bbox[1] + HEADER_TO_BODY * (bbox[2] - bbox[1])
    bbox[3] = bbox[0] + HEADER_TO_BODY * (bbox[3] - bbox[0])
    bbox = np.int0(bbox)

    bbox = in_bounds(bbox, image)

    DEBUG_display_image(image, "Corrected")

    image = four_point_transform(image, bbox.reshape(4, 2))
    output = four_point_transform(orig, bbox.reshape(4, 2) * ratio)

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


def improve_bbox_image(image):
    image = image.copy()
    image = cv2.GaussianBlur(image, (3, 3), 0)
    blackhatKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 12))
    blackhat = cv2.morphologyEx(image, cv2.MORPH_BLACKHAT, blackhatKernel)

    DEBUG_display_image(blackhat, "Blackhat", resize=False)

    gradX = cv2.Sobel(blackhat, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
    gradX = np.absolute(gradX)
    (minVal, maxVal) = (np.min(gradX), np.max(gradX))
    gradX = (255 * ((gradX - minVal) / (maxVal - minVal))).astype("uint8")
    gradX[gradX >= 180] = 255

    DEBUG_display_image(gradX, "GradX", resize=False)

    closingKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 6))
    thresh = cv2.morphologyEx(gradX, cv2.MORPH_CLOSE, closingKernel)
    thresh = cv2.threshold(thresh, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    DEBUG_display_image(thresh, "Before", resize=False)

    thresh = cv2.erode(thresh, None, iterations=1)
    thresh = cv2.dilate(thresh, None, iterations=1)

    DEBUG_display_image(thresh, "After", resize=False)

    significant = find_significant_contours(thresh)

    contour = significant[0]

    x, y, w, h = cv2.boundingRect(contour)

    pX = 10
    pY = 7
    x, y = max(x - pX, 0), max(y - pY, 0)
    w, h = min(w + (pX * 2), image.shape[1]), min(h + (pY * 2), image.shape[0])

    contour = (x, y, w, h)

    contour = np.int0(contour)

    return image[y:y + h, x:x + w].copy()


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
            if abs(angle) < 15:
                cv2.line(image, (x1, y1), (x2, y2), (255, 0, 0))
                image_angle += angle

        # Mean image angle in degrees
        image_angle /= len(lines)

    logging.debug("Document angle: %f", image_angle)
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
