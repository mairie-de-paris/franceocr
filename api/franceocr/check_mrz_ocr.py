def same_ocr_mrz(mrz_data, zones):
    last_name_is_valid = mrz_data["last_name"] == zones["last_name"]["value"]

    first_name_ocr_cut = zones["first_name"]["value"].split()
    first_name_mrz_cut = mrz_data["first_name"].split()
    first_name_is_valid = True
    for i in range(len(first_name_mrz_cut)):
        if first_name_mrz_cut[i] != first_name_ocr_cut[i]:
            first_name_is_valid = False

    return last_name_is_valid and first_name_is_valid
