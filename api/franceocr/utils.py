import cv2
import imutils

from franceocr.config import DEBUG, INFO


def display_image(image, window_name="Image", alone=True, resize=400):
    if resize is not False:
        image = imutils.resize(image, height=resize)

    cv2.imshow(window_name, image)

    if alone:
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def DEBUG_display_image(image, window_name="Image", alone=True, resize=400):
    if not DEBUG:
        return

    display_image(image, window_name, alone, resize)


def INFO_display_image(image, window_name="Image", alone=True, resize=400):
    if not INFO:
        return

    display_image(image, window_name, alone, resize)

def DEBUG_print(message):
    if not DEBUG:
        return

    print(message)
