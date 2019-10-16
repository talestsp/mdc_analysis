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

def test_ctw(sequence, depth, predict_choice_method, side_sequence=None):
    ctw = MyCTW(depth=depth, symbols=len(set(sequence)))

    pxs = ctw.prediction(seq=sequence, sideseq=side_sequence, choice_method=predict_choice_method)

    comparison_real_pred = pd.Series(pxs) == pd.Series(sequence[depth:])

    hits = pd.Series(sequence[depth:])[comparison_real_pred == True].tolist()
    misses = pd.Series(sequence[depth:])[comparison_real_pred == False].tolist()

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

def evaluation_ctw_single_partition_light_mem(tags_sequence, user_id, input_data_version, predict_choice_method,
                                    dir_name, depth, repeats_n=3, save_result=True):

    if len(tags_sequence) <= 1:
        print("sr_group size: {} \n skipping".format(len(tags_sequence)))
        raise exceptions.TooShortStopRegionGroup()

    execution_id = str(uuid.uuid4())

    for repeat_i in range(repeats_n):

        test_data = test_ctw(tags_sequence, depth=depth, predict_choice_method=predict_choice_method)

        test_data["algorithm"] = "ctw"
        test_data["trained_with"] = "same_user"
        test_data["train_size"] = len(tags_sequence)
        test_data["test_size"] = len(tags_sequence)

        if predict_choice_method == "random_dummy":
            test_data["is_dummy"] = True
        else:
            test_data["is_dummy"] = False

        test_data["pred_choice_method"] = predict_choice_method

        test_data["method"] = "single_partition"

        test_data["k"] = None
        test_data["iteration"] = repeat_i

        test_data["user_id"] = user_id

        test_data["is_distributive"] = False
        test_data["input_data_version"] = input_data_version

        test_data["test_id"] = execution_id

        if save_result:
            experiments_dao.save_execution_test_data(result_dict=test_data, filename=dir_name + "/" + test_data["test_id"] + "_i_{}".format(repeat_i))




# def evaluation_ctw_k_fold_light_mem(sequence, user_id, input_data_version, predict_choice_method,
#                                     dir_name, k, depth, side_sequence=None, save_result=True):
#
#     if len(sequence) <= 1:
#         print("sr_group size: {} \n skipping".format(len(sequence)))
#         raise exceptions.TooShortStopRegionGroup()
#
#     k_fold_partitions = k_fold_iteration(sequence, k)
#
#     execution_id = str(uuid.uuid4())
#
#     for i in range(len(k_fold_partitions)):
#         partition = k_fold_partitions[i]
#         train = partition["train"]
#         test = partition["test"]
#
#         test_data = test_ctw(sequence=sequence,
#                              side_sequence=side_sequence,
#                              depth=depth,
#                              predict_choice_method=predict_choice_method)
#
#         test_data["algorithm"] = "ctw"
#         test_data["trained_with"] = "same_user"
#         test_data["train_size"] = len(train)
#         test_data["test_size"] = len(test)
#
#         if predict_choice_method == "random_dummy":
#             test_data["is_dummy"] = True
#         else:
#             test_data["is_dummy"] = False
#
#         test_data["pred_choice_method"] = predict_choice_method
#
#         test_data["method"] = "k_fold"
#
#         test_data["k"] = k
#         test_data["iteration"] = i
#
#         test_data["user_id"] = user_id
#
#         test_data["is_distributive"] = False
#         test_data["input_data_version"] = input_data_version
#
#         test_data["test_id"] = execution_id
#
#         if save_result:
#             experiments_dao.save_execution_test_data(result_dict=test_data, filename=dir_name + "/" + test_data["test_id"] + "_i_{}".format(i))


# def evaluation_ctw_all_users_vs_one_light_mem(users_tags_sequence, input_data_version, predict_choice_method, dir_name,
#                                               depth, repeats_n=3, save_result=True):
#     lista = list(users_tags_sequence.keys())
#
#     n=0
#     for test_user in lista:
#         n += 1
#         print("n:", n, "-", "test_user:", test_user)
#
#         for repeat_i in range(repeats_n):
#             execution_id = str(uuid.uuid4())
#             train_tags = []
#
#             for train_user in users_tags_sequence.keys():
#
#                 if train_user != test_user:
#                     train_tags = train_tags + users_tags_sequence[train_user]
#
#             test_tags = users_tags_sequence[test_user]
#
#             evaluation_ctw_execute_all_users_vs_one(train_tags=train_tags, test_tags=test_tags, user_id=test_user,
#                                                     execution_id=execution_id, input_data_version=input_data_version,
#                                                     predict_choice_method=predict_choice_method, depth=depth,
#                                                     dir_name=dir_name, save_result=save_result)


# def evaluation_ctw_execute_all_users_vs_one(sequence, side_sequence, user_id, execution_id, input_data_version,
#                                             predict_choice_method, depth, dir_name, save_result):
#
#     test_data = test_ctw(sequence=sequence,
#                          side_sequence=side_sequence,
#                          depth=depth,
#                          predict_choice_method=predict_choice_method)
#
#     test_data["algorithm"] = "ctw"
#     test_data["trained_with"] = "all_other_users"
#     test_data["train_size"] = len(sequence)
#     test_data["test_size"] = len(sequence)
#
#     if predict_choice_method == "random_dummy":
#         test_data["is_dummy"] = True
#     else:
#         test_data["is_dummy"] = False
#
#     test_data["pred_choice_method"] = predict_choice_method
#
#     test_data["method"] = "all_users_vs_one"
#     test_data["user_id"] = user_id
#
#     test_data["is_distributive"] = False
#     test_data["input_data_version"] = input_data_version
#
#     test_data["test_id"] = execution_id
#
#     if save_result:
#         experiments_dao.save_execution_test_data(result_dict=test_data,
#                                                  filename=dir_name + "/" + test_data["test_id"])







########################################################
########################################################
