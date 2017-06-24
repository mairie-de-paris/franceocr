import cv2
import imutils
import franceocr
import numpy as np
import os.path

import matplotlib.pyplot as plt
from skimage.feature import match_template

from franceocr.config import IMAGE_HEIGHT, IMAGE_RATIO
from franceocr.detection import is_extracted
from franceocr.extraction import (
    extract_document,
    find_significant_contours,
    improve_bbox_image,
    improve_image,
)
from franceocr.ocr import (
    ocr_cni,
    ocr_cni_birth_date,
    ocr_cni_birth_place,
)
from franceocr.utils import DEBUG_display_image

from .mrz import process_cni_mrz


def cni_locate_zones(image, improved):
    """Locate and extract regions of interest in the image.

    Requires both the original image and the improved image.
    """

    image = imutils.resize(image, height=IMAGE_HEIGHT)
    if len(image.shape) == 3 and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    improved = imutils.resize(improved, height=IMAGE_HEIGHT)
    if len(improved.shape) == 3 and improved.shape[2] == 3:
        improved = cv2.cvtColor(improved, cv2.COLOR_BGR2GRAY)

    zones = {
        "last_name": {
            "width": 450,
            "height": 42,
            "offset_x": 0,
            "offset_y": -6,
            "after_x": 260,
            "before_x": 510,
            "after_y": 110,
            "before_y": 210,
        },
        "first_name": {
            "width": 450,
            "height": 42,
            "offset_x": 0,
            "offset_y": -2,
            "after_x": 260,
            "before_x": 510,
            "after_y": 165,
            "before_y": 265,
        },
        "birth_date": {
            "width": 180,
            "height": 42,
            "offset_x": 0,
            "offset_y": -5,
            "after_x": 480,
            "before_x": 680,
            "after_y": 240,
            "before_y": 340,
        },
        "birth_place": {
            "width": 450,
            "height": 42,
            "offset_x": 0,
            "offset_y": 22,
            "after_x": 260,
            "before_x": 510,
            "after_y": 245,
            "before_y": 345,
        },
    }

    for zone in zones:
        template = cv2.imread(os.path.dirname(__file__) + "/../templates/cni-" + zone + ".png", 0)
        templateH, templateW = template.shape
        template = imutils.resize(template, height=int(templateH * IMAGE_RATIO))
        templateH, templateW = template.shape

        xMin = int(zones[zone]["after_x"] * IMAGE_RATIO)
        xMax = int(zones[zone]["before_x"] * IMAGE_RATIO)
        yMin = int(zones[zone]["after_y"] * IMAGE_RATIO)
        yMax = int(zones[zone]["before_y"] * IMAGE_RATIO)

        DEBUG_display_image(image[yMin:yMax, xMin:xMax], "RoI", resize=False)

        result = match_template(image[yMin:yMax, xMin:xMax], template)
        ij = np.unravel_index(np.argmax(result), result.shape)
        x, y = ij[::-1]

        x += xMin
        y += yMin

        bbox = (
            x + templateW + int(zones[zone]["offset_x"] * IMAGE_RATIO),
            y + int(zones[zone]["offset_y"] * IMAGE_RATIO),
            int(zones[zone]["width"] * IMAGE_RATIO),
            int(zones[zone]["height"] * IMAGE_RATIO)
        )


        # if zone == "birth_date":
        #     cropped = image[bbox[1]:bbox[1] + bbox[3], bbox[0]:bbox[0] + bbox[2]]
        # else:
        cropped = improved[bbox[1]:bbox[1] + bbox[3], bbox[0]:bbox[0] + bbox[2]]

        # if zone == "birth_place":
        cropped = improve_bbox_image(cropped)

        zones[zone]["bbox"] = bbox
        zones[zone]["image"] = cropped

    return zones


def cni_read_zones(zones):
    """OCR-read the extracted regions of interest

    TODO
    """
    for zone in zones:
        image = zones[zone]["image"]

        if zone == "birth_date":
            zones[zone]["value"] = ocr_cni_birth_date(image)
        elif zone == "birth_place":
            zones[zone]["value"] = ocr_cni_birth_place(image)
        else:
            zones[zone]["value"] = ocr_cni(image)

    return zones


def cni_process(image):

    if not is_extracted(image):
        extracted = extract_document(image)
    else:
        extracted = image

    improved = improve_image(extracted)

    zones = cni_locate_zones(extracted, improved)

    zones = cni_read_zones(zones)

    mrz_data = process_cni_mrz(extracted)

    return {
        "mrz": mrz_data,

        "last_name_mrz": mrz_data["last_name"],
        "last_name_ocr": zones["last_name"]["value"],

        "first_name_mrz": mrz_data["first_name"],
        "first_name_ocr": zones["first_name"]["value"],

        "birth_date_mrz": "{}.{}.{}".format(
            mrz_data["birth_day"],
            mrz_data["birth_month"],
            mrz_data["birth_year"],
        ),
        "birth_date_ocr": zones["birth_date"]["value"],

        "birth_place_ocr": zones["birth_place"]["value"],
        "birth_place_corrected": zones["birth_place"]["value"],
    }