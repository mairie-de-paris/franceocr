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


import pytesseract
import re

from franceocr.config import BASEDIR
from PIL import Image


def ocr(image, lang="fra", config=None):
    image = Image.fromarray(image)

    return pytesseract.image_to_string(image, lang=lang, config=config)


def ocr_read_number(text):
    text = text \
        .replace('O', '0') \
        .replace('I', '1') \
        .replace('S', '5') \
        .replace('B', '8')

    return text


def ocr_read_text(text):
    text = text \
        .replace('0', 'O') \
        .replace('1', 'I') \
        .replace('5', 'S') \
        .replace('8', 'B')

    return text


def ocr_cni(image):
    ocr_result = ocr(
        image,
        "franceocr",
        "--oem 1 --psm 7 " + BASEDIR + "/tessconfig/cni"
    )

    ocr_result = ocr_result \
        .lstrip(":") \
        .replace(",", "") \
        .replace(".", "") \
        .strip()

    return re.sub(r" +", " ", ocr_result)


def ocr_cni_birth_date(image):
    ocr_result = ocr(
        image,
        "franceocr",
        "--oem 1 --psm 7 " + BASEDIR + "/tessconfig/cni-birth_date"
    )

    ocr_result = ocr_read_number(ocr_result)

    return ocr_result \
        .replace(' ', '') \
        .replace(',', '') \
        .replace('.', '')


def ocr_cni_birth_place(image):
    ocr_result = ocr(
        image,
        "franceocr",
        "--oem 1 --psm 7 " + BASEDIR + "/tessconfig/cni-birth_place"
    )

    no_brackets = re.sub(
        r"\(.*\)",
        "",
        ocr_result
    )

    only_alphanum = re.sub(
        r"[^a-zA-Z0-9' \-]",
        "",
        no_brackets
    )

    return only_alphanum \
        .lstrip(":") \
        .lstrip("'") \
        .strip()


def ocr_cni_mrz(image):
    ocr_result = ocr(
        image,
        "OCRB",
        "--oem 0 " + BASEDIR + "/tessconfig/cni-mrz"
    )

    return ocr_result
