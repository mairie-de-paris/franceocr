import argparse
import cv2
import imutils
import math
import numpy as np

from skimage.filters import threshold_local, threshold_minimum, threshold_otsu
from skimage.morphology import *
from skimage.exposure import *
from .transform import four_point_transform

def edge_detect(channel):
    sobelX = cv2.Sobel(channel, cv2.CV_16S, 1, 0)
    sobelY = cv2.Sobel(channel, cv2.CV_16S, 0, 1)
    sobel = np.hypot(sobelX, sobelY)

    # sobel[sobel > 255] = 255; # Some values seem to go above 255. However RGB channels has to be within 0-255

    return sobel

def find_significant_contours(image, edge_image):
    _, contours, _ = cv2.findContours(edge_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

     # From among them, find the contours with large surface area.
    significant = []
    tooSmall = edge_image.size * 5 / 100 # If contour isn't covering 5% of total area of image then it probably is too small
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > tooSmall:
            significant.append([contour, area])

            # Draw the contour on the original image
            cv2.drawContours(image, [contour], 0, (0,255,0),2, cv2.LINE_AA, maxLevel=1)

    significant.sort(key=lambda x: x[1])
    #print ([x[1] for x in significant])
    return [x[0] for x in significant]

def extract_document(image):
    ratio = image.shape[0] / 650
    orig = image.copy()
    image = imutils.resize(image, height=650)

    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    edged = np.max( np.array([ edge_detect(blurred[:,:, 0]), edge_detect(blurred[:,:, 1]), edge_detect(blurred[:,:, 2]) ]), axis=0 )
    mean = np.mean(edged)
    # Zero any value that is less than mean. This reduces a lot of noise.
    edged[edged <= mean] = 0

    # show the original image and the edge detected image
    print("STEP 1: Edge Detection")
    cv2.imshow("Image", image)
    cv2.imshow("Edged", edged)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    edged_8u = np.asarray(edged, np.uint8)

    # Find contours
    significant = find_significant_contours(image, edged_8u)

    contour = significant[0]
    # epsilon = 0.10 * cv2.arcLength(contour,True)
    # contour = cv2.approxPolyDP(contour, epsilon, True)
    contour = cv2.boxPoints(cv2.minAreaRect(contour))
    contour = np.int0(contour)

    cv2.drawContours(image, [contour], -1, (255, 0, 0), 2)
    cv2.imshow("Outline", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # apply the four point transform to obtain a top-down
    # view of the original image
    warped = four_point_transform(orig, contour.reshape(4, 2) * ratio)

    # show the original and scanned images
    print("STEP 3: Apply perspective transform")
    cv2.imshow("Original", imutils.resize(orig, height=500))
    cv2.imshow("Scanned", imutils.resize(warped, height=500))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return warped

def improve_image(image):
    # convert the image to grayscale, then threshold it
    # to give it that 'black and white' paper effect
    image = imutils.resize(image, height=650)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # initialize a rectangular and square structuring kernel
    rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 5))

    # smooth the image using a 3x3 Gaussian, then apply the blackhat
    # morphological operator to find dark regions on a light background
    image = cv2.GaussianBlur(image, (3, 3), 0)
    image = cv2.morphologyEx(image, cv2.MORPH_BLACKHAT, rectKernel)

    # cv2.imshow("Blackhat", image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    image = equalize_adapthist(image)
    image = adjust_sigmoid(image, cutoff=0.5, gain=7) * 255
    image = image.astype("uint8")
    image = cv2.bitwise_not(image)

    # Courbe pour effacer les détails
    image[image <= 50] = 50
    image[image >= 220] = 220
    image = (image - 50) / 170 * 255
    image = image.astype("uint8")

    # cv2.imshow("Filter", image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # thresh = threshold_local(image, 35, offset=10)
    # # thresh = threshold_minimum(image)
    # image = image > thresh
    # image = image.astype("uint8") * 255
    #
    # cv2.imshow("Threshold", image)

    cv2.imshow("Improved", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return image

def compute_skew(image):
    image = imutils.resize(image, height=650)
    orig = image.copy()

    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imshow("Gray", image)
    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    canny_threshold = 50
    edges = cv2.Canny(blurred, canny_threshold, canny_threshold * 3, apertureSize = 3)
    cv2.imshow("Edges", edges)
    image = cv2.bitwise_not(image, image)
    cv2.imshow("BW", image)

    rho_step = 1
    theta_step = np.pi / 180
    threshold = 100
    min_line_length = image.shape[1] * 0.6
    max_line_gap = 20
    lines = cv2.HoughLinesP(edges, rho_step, theta_step, threshold, minLineLength=min_line_length, maxLineGap=max_line_gap)

    image_angle = 0
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = math.atan2(y2 - y1, x2 - x1) / np.pi * 180
        print(angle)
        if abs(angle) < 15:
            cv2.line(orig, (x1, y1), (x2, y2), (255, 0, 0))
            image_angle += angle

    # Mean image angle in degrees
    image_angle /= len(lines)
    print("Document angle %s deg" % image_angle)

    cv2.imshow("Lines", orig)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return angle

def deskew_image(image, angle):
    rot_mat = cv2.getRotationMatrix2D((image.shape[0] / 2, image.shape[1] / 2), angle, 1)
    height = image.shape[0]
    width = image.shape[1]
    rotated = cv2.warpAffine(image, rot_mat, (width, height), flags=cv2.INTER_CUBIC)

    cv2.imshow("Rotated", imutils.resize(rotated, height=500))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return rotated

def remove_blur(image):
    cv2.imshow('Original', imutils.resize(image, height=500))

    output = denoise_bilateral(imutils.resize(image, height = 200), sigma_color=0.05, sigma_spatial=15)

    cv2.imshow("Unblurred", imutils.resize(output, height=500))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return output

def detect_text(image):
    image = imutils.resize(image, height=650)
    if len(image.shape) == 3  and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    sobel = cv2.Sobel(image, ddepth=cv2.CV_8U, dx=1, dy=0, ksize=3, scale=1, delta=0, borderType=cv2.BORDER_DEFAULT)
    thresh = cv2.threshold(sobel, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    cv2.imshow("Thresh", sobel)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    closingKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 5))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, closingKernel)
    thresh = cv2.erode(thresh, None, iterations=2)

    cv2.imshow("Thresh", thresh)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    print(contours)

    zones = []
    for contour in contours:
        if len(contour) > 0:
            contour = cv2.approxPolyDP(contour, 3, True)
            appRect = cv2.boundingRect(contour)
            x, y, w, h = appRect

            if w > h:
                zones.append(appRect)
                cv2.rectangle(image, (x, y), (x + w, y + h), 0)

    cv2.imshow("Zones", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return zones
