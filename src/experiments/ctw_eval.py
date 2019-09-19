import pandas as pd
import uuid
from src.ml.ctw import MyCTW
from src.dao import experiments_dao

def test_ctw(user_id, sequence, depth, predict_choice_method, method, input_data_version, save_result=True):
    if predict_choice_method == "DUMMY":
        predict_choice_method = "random_dummy"
        method = method + "-DUMMY"

    ctw = MyCTW(depth=depth, symbols=len(set(sequence)))
    pxs = ctw.prediction(seq=sequence, method=predict_choice_method)

    comparison_real_pred = pd.Series(pxs) == pd.Series(sequence[depth:])

    hits_freq = comparison_real_pred.value_counts()

    test_data = {"user_id": user_id,
                 "method": method,
                 "input_data_version": input_data_version,
                 "test_id": str(uuid.uuid4()),
                 "hits": pd.Series(sequence[depth:])[comparison_real_pred == True],
                 "misses": pd.Series(sequence[depth:])[comparison_real_pred == False],
                 "total_hits": hits_freq[True],
                 "total_misses": hits_freq[True],
                 "train_size": len(sequence),
                 "test_size": len(pxs),
                 "is_distributive": False,
                 "trained_with": "same_user",
                 "depth": depth,
                 "predict_choice_method": predict_choice_method
                 }

    if save_result:
        experiments_dao.save_execution_test_data(result_dict=test_data,
                                                 filename="ctw_model/" + test_data["test_id"])

