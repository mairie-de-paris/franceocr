ls -1 franceocrtrain/*.box | sed 's/franceocrtrain/franceocr_from_eng/' | sed 's/box/lstmf/' > franceocr_from_eng/franceocr.training_files.txt

ls -1 franceocreval/*.box | sed 's/franceocreval/franceocr_from_eng/' | sed 's/box/lstmf/' > franceocr_from_eng/franceocr.eval_files.txt
