import cv2
import imutils
import franceocr
import numpy as np
import os.path

import matplotlib.pyplot as plt
from skimage.feature import match_template

def cni_locate_zones(image, improved):
    image = imutils.resize(image, height=650)
    if len(image.shape) == 3  and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    improved = imutils.resize(improved, height=650)
    if len(improved.shape) == 3  and improved.shape[2] == 3:
        improved = cv2.cvtColor(improved, cv2.COLOR_BGR2GRAY)

    zones = {
        "last_name": {
            "width": 500,
            "height": 35,
            "offset_x": 0,
            "offset_y": -4,
        },
        "first_name": {
            "width": 500,
            "height": 35,
            "offset_x": 0,
            "offset_y": 0,
        },
        "birth_date": {
            "width": 180,
            "height": 35,
            "offset_x": 0,
            "offset_y": -3,
        },
        "birth_place": {
            "width": 500,
            "height": 35,
            "offset_x": 0,
            "offset_y": 30,
        },
    }

    for zone in zones:
        template = cv2.imread(os.path.dirname(__file__) + "/../templates/cni-" + zone + ".png", 0)
        templateH, templateW = template.shape

        result = match_template(image, template)
        ij = np.unravel_index(np.argmax(result), result.shape)
        x, y = ij[::-1]

        bbox = (
            x + templateW + zones[zone]["offset_x"],
            y + zones[zone]["offset_y"],
            zones[zone]["width"],
            zones[zone]["height"]
        )

        # cv2.rectangle(image, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), 255, 1)

        zones[zone]["bbox"] = bbox
        zones[zone]["image"] = improved[bbox[1]:bbox[1] + bbox[3], bbox[0]:bbox[0] + bbox[2]]

    # cv2.imshow("Matched", image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return zones
