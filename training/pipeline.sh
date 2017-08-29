# Reset temp directory
rm -rf franceocr_from_eng/
mkdir -p franceocr_from_eng/

# Add tif/box pairs to lang data
cp franceocrdata/* langdata/eng/
# cp eng.franceocr.exp0.{box,tif} langdata/eng/

# Generate training data (lstmf files)  # "DejaVu Sans"
../../tesseract/training/tesstrain.sh \
    --lang eng \
    --langdata_dir langdata \
    --linedata_only \
    --noextract_font_properties \
    --fontlist "OCRB" \
    --output_dir franceocr_from_eng \
    --training_text langdata/eng/franceocr.training_text \
    --exposures "0"

# Generate list of wanted lstmf files
./list_train.sh

# Train
./train.sh

# Once the network has converged, pack the weights
./stop_train.sh

cp franceocr_from_eng/franceocr.traineddata ../api

# Install new lang data "franceocr"
sudo cp franceocr_from_eng/franceocr.traineddata /usr/local/share/tessdata/
