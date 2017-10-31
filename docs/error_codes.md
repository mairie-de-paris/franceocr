# Error codes

- **DOCUMENT_EXTRACTION_FAILED** :  
The extraction of the document within the image failed 
(`extract_document()` function failed).

- **IMAGE_IMPROVEMENT_FAILED** :  
The improvement of the extracted image failed 
(`improve_image()` function failed).

- **IMG_SIZE_TOO_SMALL** :  
The image provided is too small, its smallest side is lower than 900 pixels. 
The image must be at least 900x900 pixels.

- **INCONSISTENT_OCR_MRZ** :  
OCR data and MRZ data don't match 
(`same_ocr_mrz()` function returned `False`).

- **INVALID_BIRTHDATE_CHECKSUM** :  
The checksum of the date of birth extracted from the MRZ (characters from 28 to 33 of the second line)
is not valid.

- **INVALID_EMIT_CHECKSUM** :  
The checksum of the first 12 characters of the second line of the MRZ is not valid.

- **INVALID_FILE_TYPE** :  
The type of the file provided is neither _jpg (JPEG)_ nor _png (PNG)_ nor _pdf (PDF)_,
and is therefore not supported.

- **INVALID_GLOBAL_CHECKSUM** :  
The checksum of the first line and the first 35 characters of the second line is not valid.

- **INVALID_LINE0_LENGTH** :  
The first line (line 0) of the MRZ is not 36 characters long as expected.

- **INVALID_LINE1_LENGTH** :  
The second line (line 1) of the MRZ is not 36 characters long as expected.

- **INVALID_MRZ_ID** :  
The first 2 characters of the first line of the MRZ are not `ID` as expected.

- **INVALID_MRZ_LINES_COUNT** :  
The MRZ data extracted does not contain 2 lines as expected.

- **INVALID_MRZ_SEX** :  
The sex character extracted from the MRZ is neither `M` (male) nor `F` (female).

- **MISSING_IMAGE_FILE** :  
The image file is missing in the image field of the HTTP POST request.

- **MRZ_EXTRACTION_FAILED** :  
The extraction of the MRZ failed 
(`cni_mrz_extract()` function failed).

- **ZONES_LOCATION_FAILED** :  
The location of the different zones in the document failed 
(`cni_locate_zone()` function failed).







