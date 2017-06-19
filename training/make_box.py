import argparse
import os.path

from pathlib import Path
from PIL import Image

parser = argparse.ArgumentParser()

parser.add_argument(
    "image_file",
    type=str,
    help="path to image file"
)

parser.add_argument(
    "xmin",
    type=int,
    help="x position of the first letter"
)

parser.add_argument(
    "string",
    type=str,
    help="string of the image"
)

parser.add_argument(
    "--ymin",
    type=int,
    help="y position of the top of the string",
    default=2
)

parser.add_argument(
    "--width",
    type=int,
    help="width of a letter",
    default=22
)

parser.add_argument(
    "--height",
    type=int,
    help="height of a letter",
    default=38
)

args = parser.parse_args()


image = Image.open(args.image_file)
image_width, image_height = image.size

box_file = Path(args.image_file).with_suffix(".box")

top = image_height - args.ymin
bottom = image_height - args.ymin - args.height

with open(box_file, 'w') as f:
    for i, letter in enumerate(args.string):
        page = 0
        left = args.xmin + i * args.width
        right = args.xmin + (i + 1) * args.width

        f.write(
            "{} {} {} {} {}\n".format(letter, left, bottom, right, top, page)
        )
