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
import numpy as np

from franceocr.config import DEBUG, INFO


def display_image(image, window_name="Image", alone=True, resize=400):
    if resize is not False:
        image = imutils.resize(image, height=resize)

    cv2.imshow(window_name, image)

    if alone:
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def DEBUG_display_image(image, window_name="Image", alone=True, resize=400):
    if DEBUG or INFO:
        display_image(image, window_name, alone, resize)


def INFO_display_image(image, window_name="Image", alone=True, resize=400):
    if INFO:
        display_image(image, window_name, alone, resize)


def in_bounds(bbox, image):
    """ Cut bbox to fit in the image """
    bbox[:, 0] = np.maximum(0, np.minimum(bbox[:, 0], image.shape[1]))
    bbox[:, 1] = np.maximum(0, np.minimum(bbox[:, 1], image.shape[0]))

    return bbox
