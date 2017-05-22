import os.path
import pytesseract

from PIL import Image, ImageFilter

def ocr(image, lang="fra", config=None):
    image = Image.fromarray(image)
    # image.filter(ImageFilter.SHARPEN)
    return pytesseract.image_to_string(image, lang=lang, config=config)

def ocr_cni(image):
    return ocr(image, "fra", "--oem 2 --psm 7 " + os.path.dirname(__file__) + "/tessconfig/cni")

def ocr_cni_birth_date(image):
    return ocr(image, "fra", "--oem 2 --psm 7 " + os.path.dirname(__file__) + "/tessconfig/cni-birth_date")

def ocr_cni_birth_place(image):
    return ocr(image, "fra", "--oem 2 --psm 7 " + os.path.dirname(__file__) + "/tessconfig/cni-birth_place")

def ocr_cni_mrz(image):
    return ocr(image, "fra", os.path.dirname(__file__) + "/tessconfig/cni-mrz")
