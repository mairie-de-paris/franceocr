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
import datetime

from flask import Blueprint, current_app, jsonify, request
from uuid import uuid4
from wand.image import Image as WandImage

from franceocr import cni_process
from franceocr.cni.exceptions import InvalidChecksumException, InvalidMRZException
from franceocr.exceptions import ImageProcessingException, InvalidOCRException

from excel_export import fill_new_line
from exceptions import InvalidUsageException
from utils import allowed_file, is_pdf, to_json

cni_blueprint = Blueprint("cni", __name__)


@cni_blueprint.errorhandler(ImageProcessingException)
@cni_blueprint.errorhandler(InvalidChecksumException)
@cni_blueprint.errorhandler(InvalidMRZException)
@cni_blueprint.errorhandler(InvalidOCRException)
def handle_errors(error):
    logging.warn("FranceOCR exception")
    response = jsonify({
        "exception": type(error).__name__,
        "code": error.code,
        "message": error.message,
    })
    response.status_code = 422
    return response


@cni_blueprint.route("/api/cni/scan", methods=["POST"])
def cni_scan():
    """
    Scan a French National Identity Card
    ---
    summary: scan a French National Identity Card
    tags:
      - cni
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: image
        type: file
        required: true
        description: a picture of a CNI card (pdf, png, or jpeg)
    responses:
      400:
        description: Bad request
        schema:
          id: APIError
          properties:
            exception:
              type: string
              description: exception name
            code:
              type: string
              description: exception code
            message:
              type: string
              description: exception message
      422:
        description: Unprocessable entity (FranceOCR processing exception)
        schema:
          id: APIError
          properties:
            exception:
              type: string
              description: exception name
            code:
              type: string
              description: exception code
            message:
              type: string
              description: exception message
      200:
        description: Scan successful
        schema:
          id: ScanOutput
          properties:
            image_path:
              type: string
              description: path to the uploaded original image
            excel_path:
              type: string
              description: path to the results Excel sheet
            data:
              description: extracted data from CNI
              schema:
                id: CNIScanOutput
                properties:
                  validated:
                    description: validated data from the scan
                    schema:
                      id: CNIValidatedData
                      properties:
                        birth_date:
                          type: string
                          description: birth date of the card's holder
                        birth_place:
                          type: string
                          description: birth place of the card's holder
                        birth_place_exists:
                          type: boolean
                          description: does the birth place of the card's holder exist?
                        birth_place_similar:
                          type: array
                          description: 5 most similar city names from OCR'd birth place
                          items:
                            schema:
                              id: SimilarCity
                              properties:
                                name:
                                  type: string
                                  description: city name
                                score:
                                  type: integer
                                  description: similarity score
                        first_name:
                          type: string
                          description: first names of the card's holder
                        last_name:
                          type: string
                          description: last name of the card's holder
                  ocr:
                    description: raw data from OCR
                    schema:
                      id: CNIOCRData
                      properties:
                        birth_date:
                          type: string
                          description: birth date of the card's holder
                        birth_place:
                          type: string
                          description: birth place of the card's holder
                        first_name:
                          type: string
                          description: first names of the card's holder
                        last_name:
                          type: string
                          description: last name of the card's holder
                  mrz:
                    description: raw data from MRZ
                    schema:
                      id: CNIMRZData
                      properties:
                        adm_code:
                          type: string
                          description: internal code from the administration of the issuing office
                        adm_code2:
                          type: string
                          description: same first three characters as `adm_code`
                        birth_day:
                          type: integer
                          description: day of birth of the card's holder
                        birth_month:
                          type: integer
                          description: month of birth of the card's holder
                        birth_year:
                          type: integer
                          description: year of birth of the card's holder
                        checksum:
                          type: integer
                          description: global checksum of the card
                        checksum_birth:
                          type: integer
                          description: checksum of the birth date
                        checksum_emission:
                          type: integer
                          description: checksum of the emission date
                        country:
                          type: string
                          description: card's emission country
                          enum:
                            - FRA
                        emission_code:
                          type: integer
                          description: assigned by the management center in chronological order in relation to the place of issue and the date of application
                        emission_month:
                          type: integer
                          description: month of emission of the card
                        emission_year:
                          type: integer
                          description: year of emission of the card
                        first_name:
                          type: string
                          description: truncated first names of the card's holder
                        id:
                          type: string
                          description: MRZ type
                          enum:
                            - ID
                        last_name:
                          type: string
                          description: truncated last name of the card's holder
                        sex:
                          type: string
                          description: sex of the card's holder
                          enum:
                            - F
                            - M

    """
    image_file = request.files.get("image")

    if not image_file:
        raise InvalidUsageException("MISSING_IMAGE_FILE", "Missing file in `image` field")

    if not allowed_file(image_file):
        raise InvalidUsageException("INVALID_FILE_TYPE", "Invalid file type")

    filename = str(uuid4()) + os.path.splitext(image_file.filename)[1]
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)

    if is_pdf(image_file):
        # Converting first page into JPG
        with WandImage(file=image_file) as img:
            with img.convert("jpg") as converted_img:
                filepath += ".jpg"
                converted_img.save(filename=filepath)
    else:
        image_file.save(filepath)

    timestamp_of_saved_image = " ({:%Y-%b-%d %H:%M})".format(datetime.datetime.now())

    # image = np.array(Image.open(image_file.stream))
    # image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    # print(image.shape)
    # print(image.mean(axis=0).mean(axis=0))

    # FIXME
    image = cv2.imread(filepath)

    if not current_app.config["KEEP_SCANS"]:
        os.remove(filepath)

    if min(image.shape[0], image.shape[1]) < 900:
        raise InvalidUsageException("IMG_SIZE_TOO_SMALL", "Image must be at least 900x900 pixels")

    excel_path = os.path.join(current_app.config["UPLOAD_FOLDER"], "exported_data.xls")

    try:
        cni_data = cni_process(image)
    except ImageProcessingException as ex:
        fill_new_line(excel_path, None, None, None, None, "Oui", ex.message_fr + timestamp_of_saved_image)
        raise ex
    else:
        fill_new_line(
            excel_path,
            cni_data["validated"]["first_name"],
            cni_data["validated"]["last_name"],
            cni_data["validated"]["birth_date"],
            cni_data["validated"]["birth_place"],
            "Non",
            None
        )

    result = {
        "data": cni_data,
        "image_path": "uploads/" + filename,
        "excel_data_path": "uploads/exported_data.xls",
    }

    return to_json(result)
