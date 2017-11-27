import logging


def same_ocr_mrz(mrz_data, zones):
    last_name_is_valid = mrz_data["last_name"][:25] == zones["last_name"]["value"][:25]

    logging.debug(
        "MRZ last name: {}; OCR last name: {}; matching {}".format(
            mrz_data["last_name"], zones["last_name"]["value"], last_name_is_valid
        )
    )

    first_names_ocr = zones["first_name"]["value"].split()
    first_names_ocr_joined = "".join(first_names_ocr)
    first_names_mrz = mrz_data["first_name"].split()
    first_names_mrz_joined = "".join(first_names_mrz)
    length_checked = min([
        len(first_names_mrz_joined),
        12
    ])
    first_name_is_valid = first_names_mrz_joined[:length_checked] == first_names_ocr_joined[:length_checked]

    logging.debug(
        "MRZ first names: {}; OCR first names: {}; matching {}".format(
            first_names_mrz, first_names_ocr, first_name_is_valid
        )
    )

    return last_name_is_valid and first_name_is_valid
