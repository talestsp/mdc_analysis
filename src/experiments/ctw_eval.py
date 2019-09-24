import pandas as pd
import uuid
from src.ml.ctw import MyCTW
from src.dao import experiments_dao
from src.exceptions import exceptions
from src.utils.others import k_fold_iteration

def is_same_sequence(seq_a, seq_b):
    if len(seq_a) != len(seq_b):
        return False

    for i in len(seq_a):
        if seq_a[i] != seq_b[i]:
            return False

    return True

def test_ctw(train_sequence, test_sequence, depth, predict_choice_method):

    ctw = MyCTW(depth=depth, symbols=len(set(test_sequence)), sidesymbols=len(set(train_sequence)))

    pxs = ctw.prediction(seq=test_sequence, sideseq=train_sequence, method=predict_choice_method)

    comparison_real_pred = pd.Series(pxs) == pd.Series(test_sequence[depth:])

    hits = pd.Series(test_sequence[depth:])[comparison_real_pred == True].tolist()
    misses = pd.Series(test_sequence[depth:])[comparison_real_pred == False].tolist()

    return {
             "test_id": str(uuid.uuid4()),
             "hits": hits,
             "misses": misses,
             "total_hits": len(hits),
             "total_misses": len(misses),
             "is_distributive": False,
             "trained_with": "same_user",
             "depth": depth,
             "predict_choice_method": predict_choice_method
             }

def evaluation_ctw_k_fold_light_mem(tags_sequence, user_id, input_data_version, predict_choice_method,
                                    dir_name, k, depth, save_result=True):

    if len(tags_sequence) <= 1:
        print("sr_group size: {} \n skipping".format(len(tags_sequence)))
        raise exceptions.TooShortStopRegionGroup()

    k_fold_partitions = k_fold_iteration(tags_sequence, k)

    execution_id = str(uuid.uuid4())

    for i in range(len(k_fold_partitions)):
        partition = k_fold_partitions[i]
        train = partition["train"]
        test = partition["test"]

        test_data = test_ctw(train, test, depth=depth, predict_choice_method=predict_choice_method)

        test_data["algorithm "]= "ctw"
        test_data["trained_with"] = "same_user"
        test_data["train_size"] = len(train)
        test_data["test_size"] = len(test)

        if predict_choice_method.lower() == "dummy":
            test_data["method"] = "k_fold-{}".format("DUMMY")

        else:
            test_data["method"] = "k_fold"

        test_data["k"] = k
        test_data["iteration"] = i

        test_data["user_id"] = user_id

        test_data["is_distributive"] = False
        test_data["input_data_version"] = input_data_version

        test_data["test_id"] = execution_id

        if save_result:
            experiments_dao.save_execution_test_data(result_dict=test_data, filename=dir_name + "/" + test_data["test_id"] + "_i_{}".format(i))
