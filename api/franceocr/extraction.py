import cv2
import imutils
import logging
import math
import numpy as np

from skimage.exposure import equalize_hist
from skimage.morphology import closing
from imutils.perspective import four_point_transform, order_points

from franceocr.config import IMAGE_WIDTH
from franceocr.utils import (
    DEBUG_display_image,
    INFO_display_image,
    in_bounds
)


def edge_detect(channel):
    sobelX = cv2.Sobel(channel, cv2.CV_16S, 1, 0, ksize=5)
    sobelY = cv2.Sobel(channel, cv2.CV_16S, 0, 1, ksize=5)
    sobel = np.hypot(sobelX, sobelY)

    return sobel


def find_significant_contours(edged_image, ratio=0.05, approx=False):
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
        if approx:
            perimeter = cv2.arcLength(contour, True)
            contour_approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)

            if len(contour_approx) == 4:
                contours[i] = contour_approx

        area = cv2.contourArea(contour)
        if area <= tooSmall:
            contours = contours[:i]
            break

    return contours


def extract_document(image):
    orig0 = image.copy()
    orig = image.copy()
    # === Beginning of the pass 0 of the extraction === #
    # Use edges to find a first approximation of the document

    orig_ratio = image.shape[1] / IMAGE_WIDTH
    image = imutils.resize(image, width=IMAGE_WIDTH)

    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    edged = np.max(np.array([
        edge_detect(blurred[:, :, 0]),
        edge_detect(blurred[:, :, 1]),
        edge_detect(blurred[:, :, 2])
    ]), axis=0)
    # edged = cv2.Laplacian()
    # Zero any value that is less than mean. This reduces a lot of noise.
    edged[edged <= np.percentile(edged, 70)] = 0

    edged_8u = np.asarray(edged, np.uint8)
    DEBUG_display_image(edged_8u, "Edged")

    # Find contours
    significant = find_significant_contours(edged_8u, approx=True)

    # Perspective correction ?
    bbox = significant[0]
    if len(bbox) != 4:
        bbox = cv2.boxPoints(cv2.minAreaRect(cv2.convexHull(bbox)))
        bbox = np.int0(bbox)

    image = four_point_transform(image, bbox.reshape(4, 2))
    DEBUG_display_image(image, "Extracted0")

    extracted_ar = image.shape[1] / image.shape[0]
    print(extracted_ar)
    if 0.65 <= extracted_ar <= 0.75 or 1.35 <= extracted_ar <= 1.6:
        orig = four_point_transform(orig, bbox.reshape(4, 2) * orig_ratio)

    # === End of the pass 0 of the extraction === #
    # === Beginning of the first pass of the extraction === #
    # Finds the blue header of the CNI to improve the extraction

    orig_ratio = orig.shape[1] / IMAGE_WIDTH
    image = imutils.resize(orig, width=IMAGE_WIDTH)

    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([210 / 2, 60, 40])
    upper_blue = np.array([260 / 2, 255, 255])
    image_blue = cv2.inRange(image_hsv, lower_blue, upper_blue)

    image_blue = cv2.GaussianBlur(image_blue, (5, 5), 0)

    DEBUG_display_image(image, "Image", alone=False)
    DEBUG_display_image(image_blue, "Blue component")

    # Clean up blue component to find orientation
    image_blue_2 = cv2.erode(image_blue, None, iterations=5)
    # blackhatKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 50))
    # image_blue_2 = cv2.morphologyEx(image_blue_2, cv2.MORPH_CLOSE, blackhatKernel)
    # image_blue_2 = cv2.threshold(image_blue_2, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    DEBUG_display_image(image_blue_2, "Blue component 2")

    # Find contours
    significant = find_significant_contours(image_blue, ratio=0)

    contour = significant[0]
    bbox = cv2.boxPoints(cv2.minAreaRect(contour))
    bbox = order_points(bbox)

    # Make sure the document has the right orientation
    accumulator = np.where(image_blue_2)
    center_x = np.median(accumulator[1])
    center_y = np.median(accumulator[0])
    print(center_x, center_y, np.mean(bbox, axis=0))

    if center_x < image.shape[1] / 3:
        logging.debug("Rotate right")
        image = imutils.rotate_bound(image, 90)
        orig = imutils.rotate_bound(orig, 90)
        # Rotate bbox 90°
        tmp = bbox[:, 0].copy()
        bbox[:, 0] = image.shape[1] - bbox[:, 1].copy()
        bbox[:, 1] = tmp

    elif center_x > 2 * image.shape[1] / 3:
        logging.debug("Rotate left")
        image = imutils.rotate_bound(image, -90)
        orig = imutils.rotate_bound(orig, -90)
        # Rotate bbox -90°
        tmp = bbox[:, 0].copy()
        bbox[:, 0] = bbox[:, 1].copy()
        bbox[:, 1] = image.shape[0] - tmp

    elif center_y > 2 * image.shape[0] / 3:
        logging.debug("Rotate 180°")
        image = imutils.rotate_bound(image, 180)
        orig = imutils.rotate_bound(orig, 180)
        # Rotate bbox 180°
        bbox = (image.shape[1], image.shape[0]) - bbox

    bbox = order_points(bbox)

    horizontal_factor = 1.03
    bbox[0], bbox[1] = bbox[1] + horizontal_factor * (bbox[0] - bbox[1]), bbox[0] + horizontal_factor * (bbox[1] - bbox[0])
    bbox[3], bbox[2] = bbox[2] + horizontal_factor * (bbox[3] - bbox[2]), bbox[3] + horizontal_factor * (bbox[2] - bbox[3])

    HEADER_TO_BODY = 1600 / 125
    right_vector = bbox[2] - bbox[1]
    left_vector = bbox[3] - bbox[0]
    height, width = image.shape[:2]
    bbox_ratio = np.nanmin([
        HEADER_TO_BODY,
        (width - bbox[1, 0]) / left_vector[0],
        (width - bbox[0, 0]) / right_vector[0],
        (height - bbox[1, 1]) / left_vector[1],
        (height - bbox[0, 1]) / right_vector[1],
    ])
    bbox_ratio = HEADER_TO_BODY
    bbox[2] = bbox[1] + bbox_ratio * left_vector
    bbox[3] = bbox[0] + bbox_ratio * right_vector
    bbox = np.int0(bbox)

    bbox = in_bounds(bbox, image)

    DEBUG_display_image(image, "Corrected")

    image = four_point_transform(image, bbox.reshape(4, 2))
    output = four_point_transform(orig, bbox.reshape(4, 2) * orig_ratio)

    DEBUG_display_image(image, "Extracted")

    # === End of the first pass of the extraction === #
    # === Deskewing === #

    # FIXME pertinent ?
    # angle = compute_skew(image)
    # image = deskew_image(image, angle)
    # output = deskew_image(output, angle)

    # === End of deskewing === #
    # === Beginning of the second pass of the extraction === #
    # ==== Remove additionnal space below the document ==== #

    aspect_ratio = image.shape[0] / image.shape[1]
    print(aspect_ratio)

    if aspect_ratio > 0.73:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edged = edge_detect(image)
        edged = np.asarray(edged, np.uint8)

        # First line from the 9/10s
        yMin = int(edged.shape[0] * 9 / 10)
        totals = np.sum(edged[yMin:], axis=1)
        totals[totals <= np.percentile(totals, 90)] = 0
        # totals[totals >= np.percentile(totals, 99)] = 0
        for y0 in range(edged.shape[0] - 1, yMin - 1, -1):
            if totals[y0 - yMin]:
                break

        if y0 == yMin:
            y0 = edged.shape[0]

        # cv2.line(edged, (0, y0), (1000, y0), (255, 255, 255), 3)

        DEBUG_display_image(edged, "Image")

        output = output[:int(y0 * orig_ratio), :]

    # === End of the second pass of the extraction === #

    INFO_display_image(orig0, "Original", alone=False)
    INFO_display_image(output, "Scanned")

    return output


def improve_image(image):
    image = imutils.resize(image, width=IMAGE_WIDTH)

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

    INFO_display_image(image, "Improved")

    return image


def improve_bbox_image(image):
    orig = image.copy()
    image = cv2.GaussianBlur(image.copy(), (3, 3), 0)
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

    significant = find_significant_contours(thresh, ratio=0)

    contour = significant[0]

    x, y, w, h = cv2.boundingRect(contour)

    pX = 12
    pY = 7
    x, y = max(x - pX, 0), max(y - pY, 0)
    w, h = min(w + (pX * 2), image.shape[1]), min(h + (pY * 2), image.shape[0])

    contour = (x, y, w, h)

    contour = np.int0(contour)

    improved = image[y:y + h, x:x + w].copy()

    DEBUG_display_image(orig, "Before", resize=False, alone=False)
    DEBUG_display_image(improved, "After", resize=False)

    return improved


def compute_skew(image):
    """Compute the skew of an image.

    Works by finding strong lines in the image and
    FIXME improve accuracy ?
    """
    image = imutils.resize(image, width=IMAGE_WIDTH)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(image, (3, 3), 0)
    gray = cv2.bitwise_not(blurred)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    DEBUG_display_image(thresh, "Gray", alone=False)

    rho_step = 1
    theta_step = 1 * np.pi / 180
    threshold = 100
    min_line_length = image.shape[1] * 0.6
    max_line_gap = 10
    lines = cv2.HoughLinesP(
        thresh[220:, :],
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
