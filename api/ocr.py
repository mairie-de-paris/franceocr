import pytesseract
from PIL import ImageFilter

def process_image(image):
    image.filter(ImageFilter.SHARPEN)
    return pytesseract.image_to_string(image)
