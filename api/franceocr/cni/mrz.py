import cv2
import imutils
import logging
import numpy as np

from skimage.filters import threshold_local
from imutils.perspective import four_point_transform

from franceocr.cni.exceptions import InvalidChecksumException, InvalidMRZException
from franceocr.exceptions import ImageProcessingException
from franceocr.extraction import find_significant_contours
from franceocr.ocr import ocr_cni_mrz, ocr_read_text, ocr_read_number
from franceocr.utils import DEBUG_display_image, INFO_display_image


def checksum_mrz(string):
    """Compute the checksum of a substring of the MRZ.

    Source: https://fr.wikipedia.org/wiki/Carte_nationale_d%27identit%C3%A9_en_France#Codage_Bande_MRZ_.28lecture_optique.29
    """

    factors = [7, 3, 1]
    result = 0
    for index, c in enumerate(string):
        if c == '<':
            val = 0
        elif '0' <= c <= '9':
            val = int(c)
        elif 'A' <= c <= 'Z':
            val = ord(c) - 55
        else:
            raise ValueError
        result += val * factors[index % 3]

    return result % 10


def cni_mrz_extract(image, improved):
    """Find and exctract the MRZ region from a CNI image.

    FIXME comments
    """
    # resize the image, and convert it to grayscale
    image = imutils.resize(image, width=900)
    if len(image.shape) == 3 and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # smooth the image using a 3x3 Gaussian, then apply the blackhat
    # morphological operator to find dark regions on a light background
    image = cv2.GaussianBlur(image, (3, 3), 0)
    blackhatKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (27, 12))
    blackhat = cv2.morphologyEx(image, cv2.MORPH_BLACKHAT, blackhatKernel)

    DEBUG_display_image(blackhat, "Blackhat")

    # compute the Scharr gradient of the blackhat image and scale the
    # result into the range [0, 255]
    gradX = cv2.Sobel(blackhat, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
    gradX = np.absolute(gradX)
    (minVal, maxVal) = (np.min(gradX), np.max(gradX))
    gradX = (255 * ((gradX - minVal) / (maxVal - minVal))).astype("uint8")

    gradX[:400] = 0

    DEBUG_display_image(gradX, "GradX")

    # apply a closing operation using the rectangular kernel to close
    # gaps in between letters -- then apply Otsu's thresholding method
    closingKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (27, 12))
    thresh = cv2.morphologyEx(gradX, cv2.MORPH_CLOSE, closingKernel)
    thresh = cv2.threshold(thresh, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    DEBUG_display_image(thresh, "Before")

    # perform another closing operation, this time using the square
    # kernel to close gaps between lines of the MRZ, then perform a
    # series of erosions to break apart connected components
    openingKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (27, 12))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, openingKernel)
    DEBUG_display_image(thresh, "After1")

    contours = cv2.findContours(
        thresh,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )[-2]

    def patch_data(contour):
        (x, y, w, h) = cv2.boundingRect(contour)
        ar = w / h
        crWidth = w / image.shape[1]
        return ar, crWidth

    def is_small_patch(contour):
        ar, crWidth = patch_data(contour)
        return ar < 5 or crWidth < 0.5

    small_patches = filter(is_small_patch, contours)
    cv2.fillPoly(thresh, list(small_patches), 0)

    DEBUG_display_image(thresh, "After1bis")

    mrzClosingKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (80, 40))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, mrzClosingKernel)
    DEBUG_display_image(thresh, "After2")

    thresh = cv2.erode(thresh, None, iterations=3)
    DEBUG_display_image(thresh, "After3")

    # during thresholding, it's possible that border pixels were
    # included in the thresholding, so let's set 5% of the left and
    # right borders to zero
    p = int(image.shape[1] * 0.05)
    thresh[:, 0:p] = 0
    thresh[:, image.shape[1] - p:] = 0

    contours = find_significant_contours(thresh)

    # loop over the contours
    for contour in contours:
        (cx, cy), (w, h), angle = cv2.minAreaRect(cv2.convexHull(contour))

        if angle < -10:
            angle += 90
            w, h = h, w
        if angle > 10:
            angle -= 90
            w, h = h, w

        ar = w / h
        crWidth = w / image.shape[1]

        logging.debug("Aspect Ratio %f Width Ratio %f Angle %f", ar, crWidth, angle)

        # check to see if the aspect ratio and coverage width are within
        # acceptable criteria
        # expected_aspect_ratio = 93.3 / (17.9 - 7.25)
        if 7 <= ar and crWidth > 0.7:
            # pad the bounding box since we applied erosions and now need
            # to re-grow it
            bbox = cv2.boxPoints(
                ((cx, cy), (1.12 * w, 1.65 * h), angle)
            )

            # extract the ROI from the image and draw a bounding box
            # surrounding the MRZ
            # mrz_image = image[y:y + h, x:x + w].copy()
            mrz_image = four_point_transform(image, bbox.reshape(4, 2))
            break

    INFO_display_image(image)

    # Further improve MRZ image quality
    thresh = threshold_local(mrz_image, 35, offset=13)
    mrz_image = mrz_image > thresh
    mrz_image = mrz_image.astype("uint8") * 255

    INFO_display_image(mrz_image, "MRZ", resize=False)

    return mrz_image


def cni_mrz_read(image):
    """Read the extracted MRZ image to a list of two 36-chars strings."""

    mrz_data = ocr_cni_mrz(image)
    mrz_data = mrz_data.replace(' ', '')
    mrz_data = mrz_data.split('\n')
    # FIlter out small strings
    mrz_data = list(filter(lambda x: len(x) >= 30, mrz_data))

    logging.debug("MRZ data: %s", mrz_data)

    return mrz_data


def mrz_read_last_name(text):
    return text.rstrip('<').replace('<', '-')


def mrz_read_first_name(text):
    return " ".join([first_name.replace('<', '-') for first_name in text.rstrip('<').split('<<')])


def mrz_read_sex(text):
    sex = text

    if sex not in ('M', 'F'):
        raise InvalidMRZException(
            "Expected sex M/F lines, got {}".format(sex)
        )

    return sex


def cni_mrz_to_dict(mrz_data):
    """Extract human-readable data from the MRZ strings."""

    if len(mrz_data) != 2:
        raise InvalidMRZException(
            "Expected 2 lines, got {}".format(len(mrz_data))
        )

    if len(mrz_data[0]) > 36 and mrz_data[0][29] == '<' and mrz_data[0][30] != '<':
        mrz_data[0] = mrz_data[0][:36]

    if len(mrz_data[0]) > 36 and mrz_data[0][-34:-31] == "FRA":
        mrz_data[0] = mrz_data[0][-36:]

    if len(mrz_data[0]) != 36:
        raise InvalidMRZException(
            "Expected line 0 to be 36-chars long, is {}".format(
                len(mrz_data[0])
            )
        )

    if len(mrz_data[1]) > 36 and mrz_data[1][34] in ('M', 'F', 'H'):
        mrz_data[1] = mrz_data[1][:36]

    if len(mrz_data[1]) > 36 and mrz_data[1][-2] in ('M', 'F', 'H'):
        mrz_data[1] = mrz_data[1][-36:]

    if len(mrz_data[1]) != 36:
        raise InvalidMRZException(
            "Expected line 1 to be 36-chars long, is {}".format(
                len(mrz_data[1])
            )
        )

    IS_NUMBER = [
        (0, 30, 36),
        (1, 0, 4),
        (1, 7, 13),
        (1, 27, 34),
        (1, 35, 36),
    ]

    for line, start, end in IS_NUMBER:
        mrz_data[line] = mrz_data[line][:start] + ocr_read_number(mrz_data[line][start:end]) + mrz_data[line][end:]

    IS_TEXT = [
        (0, 0, 30),
        (1, 13, 27),
    ]

    for line, start, end in IS_TEXT:
        mrz_data[line] = mrz_data[line][:start] + ocr_read_text(mrz_data[line][start:end]) + mrz_data[line][end:]

    if mrz_data[1][34] == 'H':
        mrz_data[1] = mrz_data[1][:34] + 'M' + mrz_data[1][35]

    logging.debug("Clean MRZ data: %s", mrz_data)

    line1, line2 = mrz_data

    values = {
        "id": line1[0:2],
        "country": line1[2:5],
        "last_name": mrz_read_last_name(line1[5:30]),
        "adm_code": line1[30:36],
        "emit_year": int(line2[0:2]),
        "emit_month": int(line2[2:4]),
        "adm_code2": line2[4:7],
        "emit_code": int(line2[7:12]),
        "checksum_emit": int(line2[12]),
        "first_name": mrz_read_first_name(line2[13:27]),
        "birth_year": int(line2[27:29]),
        "birth_month": int(line2[29:31]),
        "birth_day": int(line2[31:33]),
        "checksum_birth": int(line2[33]),
        "sex": mrz_read_sex(line2[34]),
        "checksum": int(line2[35]),
    }

    if values["id"] != "ID":
        raise InvalidMRZException(
            "Expected id to be ID, got {}".format(values["id"])
        )

    # assert(values["adm_code2"] == values["adm_code"][0:3])

    if checksum_mrz(line2[0:12]) != values["checksum_emit"]:
        raise InvalidChecksumException(
            "Invalid emit checksum"
        )
    if checksum_mrz(line2[27:33]) != values["checksum_birth"]:
        raise InvalidChecksumException(
            "Invalid birth_date checksum"
        )
    if checksum_mrz(line1 + line2[:-1]) != values["checksum"]:
        raise InvalidChecksumException(
            "Invalid global checksum"
        )

    return values


def process_cni_mrz(image, improved):
    try:
        mrz_image = cni_mrz_extract(image, improved)
    except Exception as ex:
        logging.debug("MRZ extraction failed", exc_info=True)
        raise ImageProcessingException("MRZ extraction failed") from ex

    mrz_data = cni_mrz_read(mrz_image)

    return cni_mrz_to_dict(mrz_data)
