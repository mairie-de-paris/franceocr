"""
BSD 3-Clause License

Copyright (c) 2017, Mairie de Paris
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


import cv2
import imutils
import logging
import numpy as np
import os.path

from datetime import datetime
from skimage.feature import match_template

from franceocr.cni.mrz import process_cni_mrz
from franceocr.config import IMAGE_WIDTH
from franceocr.detection import is_extracted
from franceocr.exceptions import ImageProcessingException
from franceocr.extraction import extract_document, improve_bbox_image, improve_image
from franceocr.geo import city_exists
from franceocr.ocr import ocr_cni, ocr_cni_birth_date, ocr_cni_birth_place
from franceocr.utils import DEBUG_display_image, INFO_display_image
from franceocr.check_mrz_ocr import same_ocr_mrz


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
            "before_x": 440,
            "after_y": 110,
            "before_y": 220,
        },
        "first_name": {
            "width": 700,
            "height": 60,
            "offset_x": 0,
            "offset_y": 0,
            "after_x": 320,
            "before_x": 510,
            "after_y": 180,
            "before_y": 310,
        },
        "birth_date": {
            "width": 280,
            "height": 60,
            "offset_x": -8,
            "offset_y": 5,
            "after_x": 700,
            "before_x": 920,
            "after_y": 280,
            "before_y": 450,
        },
        "birth_place": {
            "width": 700,
            "height": 60,
            "offset_x": 0,
            "offset_y": 48,
            "after_x": 330,
            "before_x": 500,
            "after_y": 280,
            "before_y": 580,
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

        INFO_display_image(cropped, "Cropped", resize=False)

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


def cni_validate_birth_year(mrz_year, ocr_year_string):
    if "19" + str(mrz_year) == ocr_year_string:
        return 1900 + mrz_year
    elif "20" + str(mrz_year) == ocr_year_string:
        return 2000 + mrz_year
    else:
        if mrz_year <= datetime.now().year % 100:
            return 2000 + mrz_year
        else:
            return 1900 + mrz_year


def cni_process(image):

    if not is_extracted(image):
        try:
            extracted = extract_document(image)
        except Exception as ex:
            logging.debug("Document extraction failed", exc_info=True)
            raise ImageProcessingException(
                "DOCUMENT_EXTRACTION_FAILED"
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
            "IMAGE_IMPROVEMENT_FAILED",
            "Image improvement failed",
            "L'amélioration du document a échoué"
        ) from ex

    try:
        zones = cni_locate_zones(extracted, improved)
    except Exception as ex:
        logging.debug("Zones location failed", exc_info=True)
        raise ImageProcessingException(
            "ZONES_LOCATION_FAILED",
            "Zones location failed",
            "La détection des zones a échoué"
        ) from ex

    zones = cni_read_zones(zones)
    mrz_data = process_cni_mrz(extracted, improved)

    last_name_corrected = mrz_data["last_name"]
    if len(last_name_corrected) == 25:
        last_name_corrected += zones["last_name"]["value"][25:]
    first_name_corrected = mrz_data["first_name"] + zones["first_name"]["value"][len(mrz_data["first_name"]):]

    birth_place_exists, birth_place_validated, similar_birth_places = city_exists(zones["birth_place"]["value"])

    birth_year_validated = cni_validate_birth_year(mrz_data["birth_year"], zones["birth_date"]["value"][-4:])

    if not(same_ocr_mrz(mrz_data, zones)):
        logging.debug("MRZ and OCR data don't match", exc_info=True)
        raise ImageProcessingException(
            "INCONSISTENT_OCR_MRZ",
            "MRZ and OCR data don't match",
            "Les données MRZ et OCR ne correspondent pas"
        )

    return {
        "mrz": mrz_data,
        "validated": {
            "birth_date": datetime(
                day=mrz_data["birth_day"],
                month=mrz_data["birth_month"],
                year=birth_year_validated,
            ).date().isoformat(),
            "birth_place": birth_place_validated,
            "birth_place_exists": birth_place_exists,
            "birth_place_similar": similar_birth_places,
            "first_name": first_name_corrected,
            "last_name": last_name_corrected,
        },
        "ocr": {
            "birth_date": zones["birth_date"]["value"],
            "birth_place": zones["birth_place"]["value"],
            "first_name": zones["first_name"]["value"],
            "last_name": zones["last_name"]["value"],

        }
    }
