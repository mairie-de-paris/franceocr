import cv2
import imutils
import numpy as np
import pytesseract

from franceocr.extraction import find_significant_contours
from franceocr.ocr import ocr_cni_mrz
from skimage.filters import threshold_adaptive


def checksum_mrz(string):
    factors = [7, 3, 1]
    result = 0
    for index, c in enumerate(string):
        if c == '<':
            val = 0
        elif '0' <= c <= '9':
            val = int(c)
        elif 'A' <= c <= 'Z':
            val = ord(c) - 55;
        else:
            raise ValueError
        result += val * factors[index % 3]

    return result % 10

def extract_mrz(image):
    # initialize a rectangular and square structuring kernel
    rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 8))
    sqKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 45))

    # resize the image, and convert it to grayscale
    image = imutils.resize(image, height=650)
    if len(image.shape) == 3  and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # smooth the image using a 3x3 Gaussian, then apply the blackhat
    # morphological operator to find dark regions on a light background
    image = cv2.GaussianBlur(image, (3, 3), 0)
    blackhat = cv2.morphologyEx(image, cv2.MORPH_BLACKHAT, rectKernel)

    cv2.imshow("Blackhat", blackhat)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # compute the Scharr gradient of the blackhat image and scale the
    # result into the range [0, 255]
    gradX = cv2.Sobel(blackhat, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
    gradX = np.absolute(gradX)
    (minVal, maxVal) = (np.min(gradX), np.max(gradX))
    gradX = (255 * ((gradX - minVal) / (maxVal - minVal))).astype("uint8")

    cv2.imshow("GradX", gradX)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # apply a closing operation using the rectangular kernel to close
    # gaps in between letters -- then apply Otsu's thresholding method
    gradX = cv2.morphologyEx(gradX, cv2.MORPH_CLOSE, rectKernel)
    thresh = cv2.threshold(gradX, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    cv2.imshow("Before", thresh)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # perform another closing operation, this time using the square
    # kernel to close gaps between lines of the MRZ, then perform a
    # series of erosions to break apart connected components
    thresh = cv2.erode(thresh, None, iterations=2)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, sqKernel)
    erodeKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
    thresh = cv2.erode(thresh, erodeKernel, iterations=4)

    cv2.imshow("After", thresh)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # during thresholding, it's possible that border pixels were
    # included in the thresholding, so let's set 5% of the left and
    # right borders to zero
    p = int(image.shape[1] * 0.05)
    thresh[:, 0:p] = 0
    thresh[:, image.shape[1] - p:] = 0

    # find contours in the thresholded image and sort them by their
    # size
    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # loop over the contours
    for contour in contours:
        # compute the bounding box of the contour and use the contour to
        # compute the aspect ratio and coverage ratio of the bounding box
        # width to the width of the image

        epsilon = 0.03 * cv2.arcLength(contour, True)
        contour = cv2.approxPolyDP(contour, epsilon, True)

        # cv2.drawContours(image, [contour], 0, (0,255,0),2, cv2.LINE_AA, maxLevel=1)

        (x, y, w, h) = cv2.boundingRect(contour)
        ar = w / float(h)
        crWidth = w / float(image.shape[1])

        print(ar, crWidth)

        # check to see if the aspect ratio and coverage width are within
        # acceptable criteria
        if 7 <= ar <= 15 and crWidth > 0.7:
            # pad the bounding box since we applied erosions and now need
            # to re-grow it
            pX = int((x + w) * 0.04)
            pY = int((y + h) * 0.05)
            (x, y) = (x - pX, y - pY)
            (w, h) = (w + (pX * 2), h + (pY * 2))

            # extract the ROI from the image and draw a bounding box
            # surrounding the MRZ
            mrz_image = image[y:y + h, x:x + w].copy()
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # break

    cv2.imshow("Image", image)
    cv2.waitKey(0)

    # Further improve MRZ image quality
    mrz_image = threshold_adaptive(mrz_image, 27, offset = 11)
    mrz_image = mrz_image.astype("uint8") * 255

    # show the output images
    cv2.imshow("ROI", mrz_image)
    cv2.imwrite("mrz_image.jpg", mrz_image)
    cv2.waitKey(0)

    return mrz_image

def read_mrz(image):
    mrz_data = ocr_cni_mrz(image)
    mrz_data = mrz_data.replace(' ', '')
    mrz_data = mrz_data.split('\n')

    print(mrz_data)

    assert(len(mrz_data) == 2)
    assert(len(mrz_data[0]) == 36)
    assert(len(mrz_data[1]) == 36)

    return mrz_data

def mrz_to_dict(mrz):
    line1, line2 = mrz

    assert(len(line1) == 36)
    assert(len(line2) == 36)

    values = {
        "id": line1[0:2],
        "country": line1[2:5],
        "last_name": line1[5:30].rstrip("<"),
        "adm_code": line1[30:36],
        "emit_year": line2[0:2],
        "emit_month": line2[2:4],
        "adm_code2": line2[4:7],
        "emit_code": line2[7:12],
        "checksum_emit": line2[12],
        "first_name": [first_name.replace("<", "-") for first_name in line2[13:27].rstrip("<").split("<<")],
        "birth_year": line2[27:29],
        "birth_month": line2[29:31],
        "birth_day": line2[31:33],
        "checksum_birth": line2[33],
        "sex": line2[34],
        "checksum": line2[35],
    }

    assert(values["id"] == "ID")
    # assert(values["adm_code2"] == values["adm_code"][0:3])
    assert(checksum_mrz(line2[0:12]) == int(values["checksum_emit"]))
    assert(checksum_mrz(line2[27:33]) == int(values["checksum_birth"]))
    assert(checksum_mrz(line1 + line2[:-1]) == int(values["checksum"]))

    return values
