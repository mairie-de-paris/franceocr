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
        "--oem 2 --psm 7 " + BASEDIR + "/tessconfig/cni"
    )

    return ocr_result \
        .lstrip(":") \
        .replace(",", "") \
        .strip()


def ocr_cni_birth_date(image):
    ocr_result = ocr(
        image,
        "franceocr",
        "--oem 2 --psm 7 " + BASEDIR + "/tessconfig/cni-birth_date"
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
        "--oem 2 --psm 7 " + BASEDIR + "/tessconfig/cni-birth_place"
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
