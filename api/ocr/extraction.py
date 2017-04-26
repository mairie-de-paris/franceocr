import argparse
import cv2
import imutils
import math
import numpy as np

from skimage.filters import threshold_local, threshold_otsu
from skimage.morphology import *
from skimage.restoration import denoise_bilateral
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

    return warped

def improve_image(image):
    # convert the image to grayscale, then threshold it
    # to give it that 'black and white' paper effect
    image = imutils.resize(image, height = 650)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = threshold_local(image, 51, offset=13)
    image = image > thresh

    cv2.imshow("Threshold", image.astype("uint8") * 255)

    # image = 1 - image
    # image = skeletonize(image)
    # image = binary_closing(image)
    # image = image.astype("uint8") * 255
    # image = binary_dilation(image)
    # image = binary_erosion(image)
    pepper = black_tophat(image)
    pepper[:120, :] = 0
    image[pepper] = 1
    image = image.astype("uint8") * 255

    # erodeKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 1))
    # image = cv2.erode(image, erodeKernel, iterations=1)
    # erodeKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 2))
    # image = cv2.erode(image, erodeKernel, iterations=1)
    # erodeKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    # image = cv2.erode(image, erodeKernel, iterations=4)

    cv2.imshow("Improved", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

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

    cv2.imshow("Rotated", imutils.resize(rotated, height = 500))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return rotated

def remove_blur(image):
    cv2.imshow('Original', imutils.resize(image, height = 500))

    output = denoise_bilateral(imutils.resize(image, height = 200), sigma_color=0.05, sigma_spatial=15)

    cv2.imshow("Unblurred", imutils.resize(output, height = 500))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return output

if __name__ == "__main__":
    image = cv2.imread("../static/img/louis2.jpg")
    document = extract_document(image)
    # remove_blur(document)
    angle = compute_skew(document)
    document = deskew_image(document, angle)
    cv2.imwrite("../static/img/extracted.jpg", document)
    document = improve_image(document)
    cv2.imwrite("../static/img/improved.jpg", document)
