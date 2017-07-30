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

# Extract english neural network weights
combine_tessdata -e /usr/local/share/tessdata/eng.traineddata franceocr_from_eng/eng.lstm

# Train
./train.sh

# Once the network has converged, pack the weights
./stop_train.sh

# Copy english trained data
cp /usr/local/share/tessdata/eng.traineddata franceocr_from_eng/franceocr.traineddata

# Replace old english weights with fine-tuned ones (trained on our tif/box pairs)
combine_tessdata -o franceocr_from_eng/franceocr.traineddata franceocr_from_eng/francocr.lstm
combine_tessdata -o franceocr_from_eng/franceocr.traineddata franceocr_from_eng/eng.lstm-*

cp franceocr_from_eng/franceocr.traineddata ../api

# Install new lang data "franceocr"
sudo cp franceocr_from_eng/franceocr.traineddata /usr/local/share/tessdata/
