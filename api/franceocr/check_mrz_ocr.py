def same_ocr_mrz(mrz_data, zones):
    last_name_is_valid = mrz_data["last_name"][:25] == zones["last_name"]["value"][:25]

    first_names_ocr = zones["first_name"]["value"].split()
    first_name_mrz_limited = len(mrz_data["first_name"]) == 13
    first_names_mrz = mrz_data["first_name"].split()
    first_name_is_valid = True
    first_names_to_check = len(first_names_mrz) if not first_name_mrz_limited else len(first_names_mrz) - 1
    for i in range(first_names_to_check):
        if first_names_mrz[i] != first_names_ocr[i]:
            first_name_is_valid = False
    if first_name_mrz_limited:
        if first_names_mrz[-1] != first_names_ocr[-1][:len(first_names_mrz[-1])]:
            first_name_is_valid = False

    return last_name_is_valid and first_name_is_valid
