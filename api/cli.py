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


import cv2
import logging
import os
import sys

from franceocr import cni_process

root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

IMAGES = {
    "Background": [
        "/home/till034/enpc/PEP/franceocr_data/uploads/3faee72b-1134-4854-b0be-8cad23514ff0.jpg",
        "/home/till034/enpc/PEP/franceocr_data/uploads/9588dabc-04d6-41bd-9846-73f10eee20bb.jpg",
    ],
    # "Perspective": [
    #     "/home/till034/enpc/PEP/franceocr_data/uploads/646c7dd5-d9ea-42a7-8869-7e957d60bbb9.jpg",
    #     "/home/till034/enpc/PEP/franceocr_data/uploads/3fe95092-8333-493c-a524-8dd046f3ead9.jpg",
    #     "/home/till034/enpc/PEP/franceocr_data/uploads/373581ba-78b3-48b0-ab91-10c5a7610cf3.jpg",
    #     "/home/till034/enpc/PEP/franceocr_data/uploads/2f446c70-5cb4-4ae1-a6d5-d94100770dba.JPG",
    #     "/home/till034/enpc/PEP/franceocr_data/uploads/423aeb3f-ccb8-4b7e-83ed-d90388758e77.jpg",
    #     "/home/till034/enpc/PEP/franceocr_data/uploads/b0ce6354-2c62-481f-860e-d9ae663ee159.jpg",
    #     "/home/till034/enpc/PEP/franceocr_data/uploads/8dc71eba-b5e2-49d6-bb8a-6a98e058c40d.jpg",
    # ],
    "Prextracted": [
        "/home/till034/enpc/PEP/franceocr_data/uploads/7c6c0165-49ea-4422-8f6a-31e712680ae8.jpg",
        "/home/till034/enpc/PEP/franceocr_data/uploads/60dc2acb-6d12-4bb3-bd75-335f4404ac79.jpg",
        "/home/till034/enpc/PEP/franceocr_data/uploads/13fb6d4f-0474-451b-8151-4e8d24102aa9.jpg",
    ],
    "Good": [
        "/home/till034/enpc/PEP/franceocr_data/uploads/df1684ce-df89-4be7-99e9-5a23460f3afe.jpg",
        "/home/till034/enpc/PEP/franceocr_data/uploads/b49b0ffd-dc20-4b81-982f-b2ed21176275.jpg",
        "/home/till034/enpc/PEP/franceocr_data/uploads/ac9d22ec-7119-4283-bbfc-fba083289100.jpg",
        "/home/till034/enpc/PEP/franceocr_data/uploads/f3a66b8c-a523-4c8e-b513-417e8dd42b43.jpg",
        "/home/till034/enpc/PEP/franceocr_data/uploads/f2c71828-bbf9-4043-9b5f-f3b3ff7b3b4b.jpg",
        "/home/till034/enpc/PEP/franceocr_data/uploads/6a666862-4898-48e3-9bc2-55eb563c21f1.JPG",
        "/home/till034/enpc/PEP/franceocr_data/uploads/92b3321d-6070-4b01-a660-4b64fba970e8.jpg",
        "/home/till034/enpc/PEP/franceocr_data/uploads/f3a66b8c-a523-4c8e-b513-417e8dd42b43.jpg",
        # "/home/till034/enpc/PEP/franceocr_data/uploads/95a42e42-6ca8-4466-bd50-3f694c9dc4c6.JPG",
        "/home/till034/enpc/PEP/franceocr_data/uploads/16ec1d5d-ba82-40f3-bfd2-5cc47a1fa86c.png",
        "/home/till034/enpc/PEP/franceocr_data/uploads/a07f06bb-9ece-400f-a3b7-a71f27d7532e.JPG",
        "/home/till034/enpc/PEP/franceocr_data/uploads/9be42e69-15c5-45b4-9e38-1ebfcd16fcff.JPG",
        "/home/till034/enpc/PEP/franceocr_data/uploads/61392818-e640-4863-8fa2-a01a95f6a239.JPG",
        "/home/till034/enpc/PEP/franceocr_data/uploads/99018d7e-6be1-4547-80ba-9694791b7dc2.jpg",
        "/home/till034/enpc/PEP/franceocr_data/uploads/0748158d-6da2-46c3-830e-54bc29e1fd4e.JPG",
        "/home/till034/enpc/PEP/franceocr_data/uploads/b71e9ce5-0391-4c93-9ee2-052837977e53.jpg",
        "/home/till034/enpc/PEP/franceocr_data/uploads/5eca1695-ecde-4990-b3f9-3acd607f1d09.JPG",
        "/home/till034/enpc/PEP/franceocr_data/uploads/dca14f3b-1514-4ac1-8c45-c2a3824848d3.jpg",
    ],
    "Non natural": [
        "/home/till034/enpc/PEP/franceocr_data/uploads/67d5cf9f-d0af-4280-92b2-441f305897a5.JPG",
        "/home/till034/enpc/PEP/franceocr_data/uploads/4932580f-3aa4-4cef-9628-13169d95e4c5.jpg",
    ],
    # "Trash": [
    #     "/home/till034/enpc/PEP/franceocr_data/uploads/c8dfbd8c-730e-4188-bf6d-11e54b7dae92.jpg",
    # ],
    "Reflets/OCR": [
        "/home/till034/enpc/PEP/franceocr_data/uploads/5a0f1b2a-4b72-40b9-987e-f805f52713e2.jpg",
    ]
}

BADS = [
    "/home/till034/enpc/PEP/franceocr_data/uploads/9be5c95f-bb48-4a9f-ab62-f0912d10f283.jpg",
    "/home/till034/enpc/PEP/franceocr_data/uploads/35bc212c-34e8-408c-85a7-ded9fe8be7c7.jpg",
    "/home/till034/enpc/PEP/franceocr_data/uploads/2c6bf620-02f9-46fd-8d97-5bdeabef4938.jpg",
    "/home/till034/enpc/PEP/franceocr_data/uploads/047566fc-19b7-464f-b712-1c480ed543f7.jpg",
    "/home/till034/enpc/PEP/franceocr_data/uploads/33accb5a-1fac-4fbe-8744-2e2556ce8af7.jpg",
    "/home/till034/enpc/PEP/franceocr_data/uploads/f7ff0e2e-927a-4d37-9432-b5bd5004e4a9.jpg",
]

if __name__ == "__main__":
    """Tool to batch process scanned CNI cards"""
    sys.stdout.write("FranceOCR utility\n")

    tries = 0
    successes = 0

    # for tag in IMAGES:
    #     print("======= {} =======".format(tag))
    #
    #     for image_path in IMAGES[tag]:

    for index, image_path in enumerate(os.listdir('/home/till034/enpc/PEP/franceocr_data/uploads')):
        image_path = "/home/till034/enpc/PEP/franceocr_data/uploads/" + image_path

        # if image_path != "/home/till034/enpc/PEP/franceocr_data/uploads/d0b95970-8ec1-4a30-b479-7c6b44b493a7.jpg":
        #     continue

        if os.path.isfile(image_path):

            print("=== {} ===".format(image_path))

            image = cv2.imread(image_path)
            tries += 1
            success = False
            try:
                cni_data = cni_process(image)
                success = True
                print("last_name_ocr", cni_data["last_name_ocr"])
                print("last_name_corrected", cni_data["last_name_corrected"])
                print("first_name_ocr", cni_data["first_name_ocr"])
                print("first_name_corrected", cni_data["first_name_corrected"])
                print("birth_date_ocr", cni_data["birth_date_ocr"])
                print("birth_place_ocr", cni_data["birth_place_ocr"])
                print("birth_place_corrected", cni_data["birth_place_corrected"])
            except Exception as ex:
                if image_path in BADS:
                    success = True
                print("Error: {}".format(ex))

            if success:
                successes += 1

            print(tries, successes, successes / tries, "SUCCESS" if success else "FAILURE")
