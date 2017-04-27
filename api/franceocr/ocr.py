import os.path
import pytesseract

from PIL import Image, ImageFilter

def process_image(image):
    image.filter(ImageFilter.SHARPEN)
    return pytesseract.image_to_string(image)

def ocr(image, lang="fra", config=None):
    image = Image.fromarray(image)
    image.filter(ImageFilter.SHARPEN)
    return pytesseract.image_to_string(image, lang="OCRB", config=config)

def ocr_cni_birthday(image, part=None):
    return ocr(image, "fra", os.path.dirname(__file__) + "/tessconfig/cni-birthday")

def ocr_cni_mrz(image):
    return ocr(image, "OCRB", os.path.dirname(__file__) + "/tessconfig/cni-mrz")
