import os.path
import pytesseract
import re

from franceocr.config import BASEDIR
from PIL import Image, ImageFilter


def ocr(image, lang="fra", config=None):
    image = Image.fromarray(image)
    # image.filter(ImageFilter.SHARPEN)
    return pytesseract.image_to_string(image, lang=lang, config=config)


def ocr_cni(image):
    ocr_result = ocr(
        image,
        "eng",
        "--oem 2 --psm 7 " + BASEDIR + "/tessconfig/cni"
    )

    return ocr_result \
        .lstrip(":") \
        .strip()


def ocr_cni_birth_date(image):
    ocr_result = ocr(
        image,
        "fra",
        "--oem 2 --psm 7 " + BASEDIR + "/tessconfig/cni-birth_date"
    )

    return ocr_result.replace(" ", "")


def ocr_cni_birth_place(image):
    ocr_result = ocr(
        image,
        "fra",
        "--oem 2 --psm 7 " + BASEDIR + "/tessconfig/cni-birth_place"
    )

    return re.sub(
        r'\(.*\)',
        '',
        ocr_result
    ).strip()


def ocr_cni_mrz(image):
    ocr_result = ocr(
        image,
        "OCRB",
        "--oem 0 " + BASEDIR + "/tessconfig/cni-mrz"
    )

    return ocr_result
