import logging


def same_ocr_mrz(mrz_data, zones):
    last_name_is_valid = mrz_data["last_name"][:25] == zones["last_name"]["value"][:25]

    # Should be 13 but when the 13th character is a "-" it is discarded (eg "Jean-Claude")
    NB_CHARS_TO_CHECK = 12
    first_names_ocr = zones["first_name"]["value"].split()
    first_name_mrz_limited = len(mrz_data["first_name"]) >= NB_CHARS_TO_CHECK
    first_names_mrz = mrz_data["first_name"].split()
    first_name_is_valid = True
    first_names_to_check = len(first_names_mrz) if not first_name_mrz_limited else len(first_names_mrz) - 1
    logging.debug("MRZ first names: {}; OCR first names: {}".format(first_names_mrz, first_names_ocr))

    for i in range(first_names_to_check):
        if first_names_mrz[i] != first_names_ocr[i]:
            first_name_is_valid = False

    if first_name_mrz_limited:
        cut_name_accumulator = 0
        for cut_name_idx, first_name in enumerate(first_names_ocr):
            cut_name_accumulator += len(first_name)
            if cut_name_accumulator >= NB_CHARS_TO_CHECK:
                break

        if first_names_mrz[-1] != first_names_ocr[cut_name_idx][:len(first_names_mrz[-1])]:
            first_name_is_valid = False

    return last_name_is_valid and first_name_is_valid
