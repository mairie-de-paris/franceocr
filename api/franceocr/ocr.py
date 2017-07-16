import pyocr
import pyocr.builders
import pytesseract
import re

from franceocr.config import BASEDIR
from PIL import Image


def ocr(image, lang="fra", config=None):
    image = Image.fromarray(image)

    return pytesseract.image_to_string(image, lang=lang, config=config)


def ocr2(image, lang="fra", config=None):
    image = Image.fromarray(image)
    tools = pyocr.get_available_tools()
    # The tools are returned in the recommended order of usage
    tool = tools[1]

    return tool.image_to_string(
        image,
        lang=lang,
        builder=pyocr.builders.TextBuilder()
    )


def ocr_cni(image):
    ocr_result = ocr(
        image,
        "franceocr",
        "--oem 2 --psm 7 " + BASEDIR + "/tessconfig/cni"
    )

    return ocr_result \
        .lstrip(":") \
        .strip()


def ocr_cni_birth_date(image):
    ocr_result = ocr(
        image,
        "franceocr",
        "--oem 2 --psm 7 " + BASEDIR + "/tessconfig/cni-birth_date"
    )

    return ocr_result.replace(" ", "").replace(',', '').replace('.', '')


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
