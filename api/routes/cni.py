import cv2
import logging
import os

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
    logging.warn("FranceOCR exception", exc_info=True)
    response = jsonify({
        "exception": type(error).__name__,
        "message": error.args[0],
    })
    response.status_code = 422
    return response


@cni_blueprint.route("/api/cni/scan", methods=["POST"])
def cni_scan():
    """
    Scan a French National Identity Card
    ---
    tags:
      - cni
    parameters:
      - in: image
        name: image
        type: file
    responses:
      201:
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
                          description: qzd
                        adm_code2:
                          type: string
                          description: qzd
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
                          description: qzd
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
        raise InvalidUsageException("No file provided")

    if not allowed_file(image_file):
        raise InvalidUsageException("Invalid file type")

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

    # image = np.array(Image.open(image_file.stream))
    # image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    # print(image.shape)
    # print(image.mean(axis=0).mean(axis=0))

    # FIXME
    image = cv2.imread(filepath)

    if min(image.shape[0], image.shape[1]) < 900:
        raise InvalidUsageException("Image must be at least 900x900 pixels")

    excel_path = os.path.join(current_app.config["UPLOAD_FOLDER"], "exported_data.xls")

    try:
        cni_data = cni_process(image)
    except ImageProcessingException as ex:
        error_message_fr = ex.args[1] if len(ex.args) > 1 else ex.args[0]
        fill_new_line(excel_path, None, None, None, None, "Oui", error_message_fr)
        raise ex

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
