import cv2
import imutils
import numpy as np
import os.path

import matplotlib.pyplot as plt
from skimage.feature import match_template

def cni_locate_zones(image):
    image = imutils.resize(image, height=650)
    if len(image.shape) == 3  and image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    template = cv2.imread(os.path.dirname(__file__) + "/../templates/cni.png", 0)
    templateH, templateW = template.shape

    result = match_template(image, template)
    result = result[:200, :200]
    ij = np.unravel_index(np.argmax(result), result.shape)
    x, y = ij[::-1]

    top_left = (x, y)
    bottom_right = (top_left[0] + templateW, top_left[1] + templateH)

    cv2.rectangle(image, top_left, bottom_right, 255, 2)
    top_left = (x - 7, y - 14)

    zones = {
        "card_number": (top_left[1] + 63, top_left[0] + 345, 35, 210),
        "last_name": (top_left[1] + 98, top_left[0] + 306, 42, 461),
        "first_name": (top_left[1] + 168, top_left[0] + 345, 37, 422),
        "sex": (top_left[1] + 229, top_left[0] + 306, 34, 39),
        "birth_date": (top_left[1] + 229, top_left[0] + 553, 34, 214),
        "birth_place": (top_left[1] + 263, top_left[0] + 276, 34, 491),
    }

    for zone in zones:
        y, x, h, w = zones[zone]
        cv2.rectangle(image, (x, y), (x + w, y + h), 255, 2)

    cv2.imshow("Matched", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
