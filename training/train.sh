lstmtraining \
    --train_listfile franceocr_from_eng/franceocr.training_files.txt \
    --continue_from franceocr_from_eng/eng.lstm \
    --model_output franceocr_from_eng/francocr \
    --target_error_rate 0.01 \
    --debug_interval -1
