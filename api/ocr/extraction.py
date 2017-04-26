import argparse
import cv2
import imutils
import math
import numpy as np

from skimage.filters import threshold_adaptive
from transform import four_point_transform

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
    ratio = image.shape[0] / 500.0
    orig = image.copy()
    image = imutils.resize(image, height = 500)

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
    cv2.imshow("Original", imutils.resize(orig, height = 650))
    cv2.imshow("Scanned", imutils.resize(warped, height = 650))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    cv2.imwrite("../static/img/extracted.jpg", warped)

    return warped

def improve_image(image):
    # convert the image to grayscale, then threshold it
    # to give it that 'black and white' paper effect
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = threshold_adaptive(image, 51, offset = 10)
    image = image.astype("uint8") * 255

    cv2.imwrite("../static/img/improved.jpg", image)
    cv2.imshow("Scanned", imutils.resize(image, height = 650))
    cv2.waitKey(0)

    return image

def compute_skew(image):
    image = imutils.resize(image, height = 500)
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
    min_line_length = image.shape[1] * 3.7
    max_line_gap = 20
    lines = cv2.HoughLinesP(edges, rho_step, theta_step, threshold, min_line_length, max_line_gap)

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
    print(image_angle)

    cv2.imshow("Lines", orig)
    cv2.waitKey(0)

    return angle

if __name__ == "__main__":
    image = cv2.imread("../static/img/louis4.jpg")
    document = extract_document(image)
    document = compute_skew(document)
    # document = improve_image(document)
