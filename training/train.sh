combine_tessdata -e /usr/local/share/tessdata/eng.traineddata \
    franceocr_from_eng/eng.lstm

lstmtraining \
    --model_output franceocr_from_eng/franceocr \
    --continue_from franceocr_from_eng/eng.lstm \
    --traineddata /usr/local/share/tessdata/eng.traineddata \
    --train_listfile franceocr_from_eng/franceocr.training_files.txt \
    --eval_listfile franceocr_from_eng/franceocr.eval_files.txt \
    --target_error_rate 0.1
    # --debug_interval -1
    # --max_iterations 400 \
