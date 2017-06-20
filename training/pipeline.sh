rm -rf franceocr_from_eng/
mkdir -p franceocr_from_eng/

cp franceocrdata/eng.franceocr*.tif langdata/eng/
cp franceocrdata/eng.franceocr*.box langdata/eng/

../../tesseract/training/tesstrain.sh \
    --lang eng \
    --langdata_dir langdata \
    --linedata_only \
    --noextract_font_properties \
    --fontlist "DejaVu Sans" \
    --output_dir franceocr_from_eng \
    --training_text langdata/eng/franceocr.training_text \
    --exposures "0"

#./make_lstmf.sh

./list_train.sh

combine_tessdata -e /usr/local/share/tessdata/eng.traineddata franceocr_from_eng/eng.lstm

./train.sh
./stop_train.sh

cp /usr/local/share/tessdata/eng.traineddata franceocr_from_eng/franceocr.traineddata

combine_tessdata -o franceocr_from_eng/franceocr.traineddata franceocr_from_eng/francocr.lstm
combine_tessdata -o franceocr_from_eng/franceocr.traineddata franceocr_from_eng/eng.lstm-*

sudo cp franceocr_from_eng/franceocr.traineddata /usr/local/share/tessdata/
