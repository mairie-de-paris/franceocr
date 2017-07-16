import cv2
import imutils
import logging
import numpy as np
import os.path

from skimage.feature import match_template

from franceocr.cni.mrz import process_cni_mrz
from franceocr.config import IMAGE_WIDTH
from franceocr.detection import is_extracted
from franceocr.exceptions import ImageProcessingException
from franceocr.extraction import extract_document, improve_bbox_image, improve_image
from franceocr.geo import city_exists
from franceocr.ocr import ocr_cni, ocr_cni_birth_date, ocr_cni_birth_place
from franceocr.utils import DEBUG_display_image, INFO_display_image


def cni_locate_zones(image, improved):
    """Locate and extract regions of interest in the image.

    Requires both the original image and the improved image.
    """

    image = imutils.resize(image, width=IMAGE_WIDTH)
    if len(image.shape) == 3 and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cv2.imwrite("template.png", image)

    improved = imutils.resize(improved, width=IMAGE_WIDTH)
    if len(improved.shape) == 3 and improved.shape[2] == 3:
        improved = cv2.cvtColor(improved, cv2.COLOR_BGR2GRAY)

    zones = {
        "last_name": {
            "width": 700,
            "height": 60,
            "offset_x": -6,
            "offset_y": -4,
            "after_x": 320,
            "before_x": 410,
            "after_y": 120,
            "before_y": 200,
        },
        "first_name": {
            "width": 700,
            "height": 60,
            "offset_x": 0,
            "offset_y": 0,
            "after_x": 320,
            "before_x": 480,
            "after_y": 200,
            "before_y": 280,
        },
        "birth_date": {
            "width": 280,
            "height": 60,
            "offset_x": -8,
            "offset_y": 5,
            "after_x": 720,
            "before_x": 900,
            "after_y": 330,
            "before_y": 430,
        },
        "birth_place": {
            "width": 700,
            "height": 60,
            "offset_x": 0,
            "offset_y": 48,
            "after_x": 350,
            "before_x": 475,
            "after_y": 330,
            "before_y": 560,
        },
    }

    for zone in zones:
        template = cv2.imread(
            os.path.dirname(__file__) + "/../templates/cni-" + zone + ".png", 0
        )
        templateH, templateW = template.shape

        xMin = int(zones[zone]["after_x"])
        xMax = int(zones[zone]["before_x"]) + templateW
        yMin = int(zones[zone]["after_y"])
        yMax = int(zones[zone]["before_y"]) + templateH

        DEBUG_display_image(image[yMin:yMax, xMin:xMax], "RoI", resize=False)

        result = match_template(image[yMin:yMax, xMin:xMax], template)
        ij = np.unravel_index(np.argmax(result), result.shape)
        x, y = ij[::-1]

        x += xMin
        y += yMin

        bbox = (
            x + templateW + int(zones[zone]["offset_x"]),
            y + int(zones[zone]["offset_y"]),
            int(zones[zone]["width"]),
            int(zones[zone]["height"])
        )

        # if zone == "birth_date":
        #     cropped = image[bbox[1]:bbox[1] + bbox[3], bbox[0]:bbox[0] + bbox[2]]
        # else:
        cropped = improved[bbox[1]:bbox[1] + bbox[3], bbox[0]:bbox[0] + bbox[2]]

        # if zone == "birth_place":
        cropped = improve_bbox_image(cropped)

        DEBUG_display_image(cropped, "Cropped", resize=False)

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
        try:
            extracted = extract_document(image)
        except Exception as ex:
            logging.debug("Document extraction failed", exc_info=True)
            raise ImageProcessingException(
                "Document extraction failed",
                "L'extraction du document a échoué"
            ) from ex
    else:
        extracted = image

    try:
        improved = improve_image(extracted)
    except Exception as ex:
        logging.debug("Image improvement failed", exc_info=True)
        raise ImageProcessingException(
            "Image improvement failed",
            "L'amélioration du document a échoué"
        ) from ex

    try:
        zones = cni_locate_zones(extracted, improved)
    except Exception as ex:
        logging.debug("Zones location failed", exc_info=True)
        raise ImageProcessingException(
            "Zones location failed",
            "La détection des zones a échoué"
        ) from ex

    zones = cni_read_zones(zones)
    mrz_data = process_cni_mrz(extracted, improved)
    birth_place_exists, birth_place_corrected, similar_birth_places = city_exists(zones["birth_place"]["value"])

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
        "birth_place_corrected": birth_place_corrected,
        "birth_place_exists": birth_place_exists,
        "birth_place_similar": similar_birth_places,
    }
