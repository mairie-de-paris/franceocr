import sys
import pytesseract

from utils import get_image


if __name__ == "__main__":
    """Tool to test the raw output of pytesseract with a given input URL"""
    sys.stdout.write("A simple OCR utility\n")
    image = get_image('static/img/CNI.jpg')
    sys.stdout.write("The raw output from tesseract with no processing is:\n\n")
    sys.stdout.write("-----------------BEGIN-----------------\n")
    sys.stdout.write(pytesseract.image_to_string(image) + "\n")
    sys.stdout.write("------------------END------------------\n")
