lstmtraining \
    --model_output franceocr_from_eng/francocr \
    --continue_from franceocr_from_eng/francocr_checkpoint \
    --traineddata /usr/local/share/tessdata/eng.traineddata \
    --train_listfile franceocr_from_eng/franceocr.training_files.txt \
    --target_error_rate 0.001 \
    --debug_interval -1
