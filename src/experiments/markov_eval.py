import uuid
from ast import literal_eval

import src.ml.markov as mk
from src.utils.others import k_fold_iteration
from src.utils.metrics import jaccard
from src.exceptions import exceptions
from src.dao import experiments_dao
from src.entity.stop_region import StopRegionGroup
from src.utils.others import partition_dict_by_keys_one_vs_all

EQUAL_DESTINATION_PROBA = "EQUAL_DESTINATION_PROBA"

def is_valid_state(state):
    if state == "[]" or state == []:
        return False
    else:
        return True

def predict_distributive_tags(predictor, current_state_list):
    next_state_pred_list = []

    for state in current_state_list:
        try:
            next_state = predictor.next_state(state)
            next_state_pred_list.append(next_state)

        except exceptions.StateNotPresentInTrainAsOrigin:
            pass

    if len(next_state_pred_list) == 0:
        raise exceptions.StateNotPresentInTrainAsOrigin()

    return next_state_pred_list

def predict_tags(predictor, current_state):
    return literal_eval(predictor.next_state(current_state))

def markov_transition_probabilities(train, is_distributive, random_dummy_mode=None):
    if is_distributive:
        trans_proba = mk.distributive_transition_probabilities(train)
    else:
        trans_proba = mk.transition_probabilities(train)

    if not random_dummy_mode is None:
        trans_proba = mk.equalize_transition_prob(trans_proba)

    return mk.to_dict(trans_proba)

def markov_cluster_transition_probabilities(train, is_distributive, random_dummy_mode=None):
    if is_distributive:
        trans_proba = mk.distributive_transition_probabilities(train)
    else:
        trans_proba = mk.transition_probabilities(train)

    if not random_dummy_mode is None:
        trans_proba = mk.equalize_transition_prob(trans_proba)

    return mk.to_dict(trans_proba)

def test_markov(train, test, is_distributive, random_dummy_mode=None):
    if is_distributive:
        trans_proba = mk.distributive_transition_probabilities(train)
    else:
        trans_proba = mk.transition_probabilities(train)

    if not random_dummy_mode is None:
        trans_proba = mk.equalize_transition_prob(trans_proba)

    trans_proba_dict = mk.to_dict(trans_proba)

    return do_markov_test(trans_proba_dict=trans_proba_dict,
                           test=test,
                           is_distributive=is_distributive)

def test_markov_cluster(train_cluster, test, is_distributive, random_dummy_mode=None):
    if is_distributive:
        trans_proba = mk.cluster_transition_probabilities(train_cluster)
    else:
        trans_proba = mk.cluster_transition_probabilities(train_cluster)

    if not random_dummy_mode is None:
        trans_proba = mk.equalize_transition_prob(trans_proba)

    trans_proba_dict = mk.to_dict(trans_proba)

    return do_markov_test(trans_proba_dict=trans_proba_dict,
                           test=test,
                           is_distributive=is_distributive)

def test_markov_cluster_multi_trip(train_trips, test_trips):
    transition_proba = mk.cluster_transition_probabilities(train_trips)
    transition_proba_dict = mk.to_dict(transition_proba)

    return do_markov_test_multi_trip(trans_proba_dict=transition_proba_dict,
                                     test_trips=test_trips,
                                     is_distributive=False)

def do_markov_test_multi_trip(trans_proba_dict, test_trips, is_distributive,):

    predictor = mk.MarkovPredictor().fit(trans_proba_dict)

    hits = []
    misses = []
    states_not_trained_as_origin = []
    partial_hits = []

    for test in test_trips:

        for test_i in range(len(test[0:-1])):
            current_state_list = test[test_i]
            next_state_real_list = test[test_i + 1]

            if not is_valid_state(current_state_list) or not is_valid_state(next_state_real_list):
                continue

            next_state_real = str(next_state_real_list)

            try:
                if is_distributive:
                    next_state_pred_list = predict_distributive_tags(predictor, current_state_list)

                else:
                    next_state_pred_list = predict_tags(predictor, str(current_state_list))

            except exceptions.StateNotPresentInTrainAsOrigin:
                states_not_trained_as_origin.append(str(current_state_list))
                partial_hits.append(0)
                misses.append({"real": next_state_real, "pred": None})
                continue

            partial_hits.append(jaccard(next_state_real_list, next_state_pred_list))

            if set(next_state_real_list) == set(next_state_pred_list):
                hits.append(next_state_real)
            else:
                misses.append({"real": next_state_real, "pred": str(next_state_pred_list)})

    return {"total_hits": len(hits),
            "total_misses": len(misses),
            "total_states_not_trained_as_origin": len(states_not_trained_as_origin),
            "hits": hits,
            "misses": misses,
            "states_not_trained_as_origin": states_not_trained_as_origin,
            "partial_hits": partial_hits
            }

def do_markov_test(trans_proba_dict, test, is_distributive,):

    predictor = mk.MarkovPredictor().fit(trans_proba_dict)

    hits = []
    misses = []
    states_not_trained_as_origin = []
    partial_hits = []

    for test_i in range(len(test[0:-1])):
        current_state_list = test[test_i]
        next_state_real_list = test[test_i + 1]

        if not is_valid_state(current_state_list) or not is_valid_state(next_state_real_list):
            continue

        next_state_real = str(next_state_real_list)

        try:
            if is_distributive:
                next_state_pred_list = predict_distributive_tags(predictor, current_state_list)

            else:
                next_state_pred_list = predict_tags(predictor, str(current_state_list))

        except exceptions.StateNotPresentInTrainAsOrigin:
            states_not_trained_as_origin.append(str(current_state_list))
            partial_hits.append(0)
            misses.append({"real": next_state_real, "pred": None})
            continue

        partial_hits.append(jaccard(next_state_real_list, next_state_pred_list))

        if set(next_state_real_list) == set(next_state_pred_list):
            hits.append(next_state_real)
        else:
            misses.append({"real": next_state_real, "pred": str(next_state_pred_list)})

    return {"total_hits": len(hits),
            "total_misses": len(misses),
            "total_states_not_trained_as_origin": len(states_not_trained_as_origin),
            "hits": hits,
            "misses": misses,
            "states_not_trained_as_origin": states_not_trained_as_origin,
            "partial_hits": partial_hits
            }


def evaluation_markov_single_partition_light_mem(tags_sequence, user_id, input_data_version,
                                                 dir_name, repeats_n=3, is_distributive=False, random_dummy_mode=None, save_result=True):

    if len(tags_sequence) <= 1:
        print("sr_group size: {} \n skipping".format(len(tags_sequence)))
        raise exceptions.TooShortStopRegionGroup()

    execution_id = str(uuid.uuid4())

    for repeat_i in range(repeats_n):

        test_data = test_markov(train=tags_sequence, test=tags_sequence, is_distributive=is_distributive, random_dummy_mode=random_dummy_mode)

        test_data["algorithm"] = "markov"
        test_data["trained_with"] = "same_user"
        test_data["train_size"] = len(tags_sequence)
        test_data["test_size"] = len(tags_sequence)

        if random_dummy_mode is None:
            test_data["is_dummy"] = False
        else:
            test_data["is_dummy"] = True

        test_data["method"] = "single_partition"

        test_data["k"] = None
        test_data["iteration"] = repeat_i

        test_data["user_id"] = user_id

        test_data["is_distributive"] = is_distributive
        test_data["input_data_version"] = input_data_version

        test_data["test_id"] = execution_id

        if save_result:
            experiments_dao.save_execution_test_data(result_dict=test_data,
                                                     filename=dir_name + "/" + test_data["test_id"] + "_i_{}".format(repeat_i))

def evaluation_markov_cluster_light_mem(cluster, test_user_id, input_data_version, cluster_version,
                                        dir_name, repeats_n=3, is_distributive=False,
                                        random_dummy_mode=None, save_result=True):

    execution_id = str(uuid.uuid4())

    if len(cluster) <= 1:
        raise exceptions.ClusterSizeInadequate

    user_tags, rest_cluster = partition_dict_by_keys_one_vs_all(a_dict=cluster, split_key=test_user_id)

    for repeat_i in range(repeats_n):

        test_data = test_markov_cluster(train_cluster=[rest_cluster[user_id] for user_id in rest_cluster.keys()],
                                        test=user_tags,
                                        is_distributive=is_distributive,
                                        random_dummy_mode=random_dummy_mode)

        test_data["algorithm"] = "markov"
        test_data["trained_with"] = "cluster"
        test_data["train_size"] = sum([len(rest_cluster[train_user_id]) for train_user_id in rest_cluster.keys()])
        test_data["test_size"] = len(user_tags)

        if random_dummy_mode is None:
            test_data["is_dummy"] = False
        else:
            test_data["is_dummy"] = True

        test_data["method"] = "cluster"
        test_data["cluster_size"] = len(cluster)

        test_data["k"] = None
        test_data["iteration"] = repeat_i

        test_data["user_id"] = test_user_id
        test_data["multi_trip"] = False

        test_data["is_distributive"] = is_distributive
        test_data["input_data_version"] = input_data_version
        test_data["cluster_version"] = cluster_version

        test_data["test_id"] = execution_id

        if save_result:
            experiments_dao.save_execution_test_data(result_dict=test_data,
                                                     filename=dir_name + "/" + test_data["test_id"] + "_i_{}".format(repeat_i))

def evaluation_markov_cluster_multi_trip(cluster, test_user_id, input_data_version, cluster_version,
                                        dir_name, repeats_n=3, is_distributive=False,
                                        random_dummy_mode=None, save_result=True):

    execution_id = str(uuid.uuid4())

    if len(cluster) <= 1:
        raise exceptions.ClusterSizeInadequate

    user_tags, rest_cluster = partition_dict_by_keys_one_vs_all(a_dict=cluster, split_key=test_user_id)

    for repeat_i in range(repeats_n):

        test_data = test_markov_cluster_multi_trip(train_trips=[rest_cluster[user_id] for user_id in rest_cluster.keys()],
                                                   test_trips=user_tags)

        test_data["algorithm"] = "markov"
        test_data["trained_with"] = "cluster"
        test_data["train_size"] = sum([len(rest_cluster[train_user_id]) for train_user_id in rest_cluster.keys()])
        test_data["test_size"] = len(user_tags)

        if random_dummy_mode is None:
            test_data["is_dummy"] = False
        else:
            test_data["is_dummy"] = True

        test_data["method"] = "cluster"
        test_data["cluster_size"] = len(cluster)

        test_data["k"] = None
        test_data["iteration"] = repeat_i

        test_data["user_id"] = test_user_id
        test_data["multi_trip"] = True

        test_data["is_distributive"] = is_distributive
        test_data["input_data_version"] = input_data_version
        test_data["cluster_version"] = cluster_version

        test_data["test_id"] = execution_id

        if save_result:
            experiments_dao.save_execution_test_data(result_dict=test_data,
                                                     filename=dir_name + "/" + test_data["test_id"] + "_i_{}".format(repeat_i))



def evaluation_markov_k_fold(sr_group, input_data_version, dir_name, k=5, is_distributive=False, random_dummy_mode=None, save_result=True):
    if sr_group.size() <= 1:
        print("sr_group size: {} \n skipping".format(sr_group.size()))
        raise exceptions.TooShortStopRegionGroup()

    tags_sequence = sr_group.sequence_stop_region_tags()["tag"].tolist()

    evaluation_markov_k_fold_light_mem(tags_sequence, sr_group.stop_region_list[0].user_id, dir_name=dir_name,
                                       input_data_version=input_data_version, k=k, is_distributive=is_distributive,
                                       random_dummy_mode=random_dummy_mode, save_result=save_result)


def evaluation_markov_k_fold_light_mem(tags_sequence, user_id, input_data_version, dir_name, k=5, is_distributive=False, random_dummy_mode=None, save_result=True):
    if len(tags_sequence) <= 1:
        print("sr_group size: {} \n skipping".format(len(tags_sequence)))
        raise exceptions.TooShortStopRegionGroup()

    k_fold_partitions = k_fold_iteration(tags_sequence, k)

    execution_id = str(uuid.uuid4())

    for i in range(len(k_fold_partitions)):
        partition = k_fold_partitions[i]
        train = partition["train"]
        test = partition["test"]

        test_data = test_markov(train, test, is_distributive=is_distributive, random_dummy_mode=random_dummy_mode)

        test_data["algorithm"] = "markov"
        test_data["trained_with"] = "same_user"
        test_data["train_size"] = len(train)
        test_data["test_size"] = len(test)

        if random_dummy_mode is None:
            test_data["is_dummy"] = True
        else:
            test_data["is_dummy"] = False

        test_data["method"] = "k_fold"

        test_data["k"] = k
        test_data["iteration"] = i

        test_data["user_id"] = user_id

        test_data["is_distributive"] = is_distributive
        test_data["input_data_version"] = input_data_version

        test_data["test_id"] = execution_id

        if save_result:
            experiments_dao.save_execution_test_data(result_dict=test_data, filename=dir_name + "/" + test_data["test_id"] + "_i_{}".format(i))


def evaluation_markov_all_users_vs_one(user_stop_region_group, input_data_version, dir_name, is_distributive=False,
                                       random_dummy_mode=None, repeats_n=3, save_result=True):
    lista = list(user_stop_region_group.keys())
    for test_user in lista:

        print(test_user)
        for repeat_i in range(repeats_n):

            execution_id = str(uuid.uuid4())
            train_tags = []

            for train_user in user_stop_region_group.keys():
                sr_group = StopRegionGroup(user_stop_region_group[train_user], agglutinate_stop_regions=True)

                if train_user != test_user:
                    train_tags = train_tags + sr_group.sequence_stop_region_tags()["tag"].tolist()

            sr_group_test = StopRegionGroup(user_stop_region_group[test_user], agglutinate_stop_regions=True)
            test_tags = sr_group_test.sequence_stop_region_tags()["tag"].tolist()

            user_id = sr_group_test.stop_region_list[0].user_id

            execute_evaluation_markov_all_users_vs_one(train_tags=train_tags, test_tags=test_tags, user_id=user_id, execution_id=execution_id,
                                                       input_data_version=input_data_version, is_distributive=is_distributive, random_dummy_mode=random_dummy_mode,
                                                       dir_name=dir_name, save_result=save_result)

def evaluation_markov_all_users_vs_one_light_mem(users_tags_sequence, input_data_version, dir_name,
                                                 is_distributive=False, random_dummy_mode=None, repeats_n=3,
                                                 save_result=True):
    lista = list(users_tags_sequence.keys())
    n=0
    for test_user in lista:
        n += 1
        print("n:", n, "-", "test_user:", test_user)

        for repeat_i in range(repeats_n):
            execution_id = str(uuid.uuid4())
            train_tags = []

            for train_user in users_tags_sequence.keys():

                if train_user != test_user:
                    train_tags = train_tags + users_tags_sequence[train_user]

            test_tags = users_tags_sequence[test_user]

            execute_evaluation_markov_all_users_vs_one(train_tags=train_tags, test_tags=test_tags, user_id=test_user, execution_id=execution_id,
                                                       input_data_version=input_data_version, is_distributive=is_distributive, random_dummy_mode=random_dummy_mode,
                                                       dir_name=dir_name, save_result=save_result)

def execute_evaluation_markov_all_users_vs_one(train_tags, test_tags, user_id, execution_id, input_data_version,
                                               is_distributive, random_dummy_mode, dir_name, save_result):

    test_data = test_markov(train_tags, test_tags, is_distributive=is_distributive, random_dummy_mode=random_dummy_mode)

    test_data["algorithm"] = "markov"
    test_data["trained_with"] = "all_other_users"
    test_data["train_size"] = len(train_tags)
    test_data["test_size"] = len(test_tags)

    if random_dummy_mode is None:
        test_data["is_dummy"] = True
    else:
        test_data["is_dummy"] = False

    test_data["method"] = "all_users_vs_one"
    test_data["user_id"] = user_id

    test_data["is_distributive"] = is_distributive
    test_data["input_data_version"] = input_data_version

    test_data["test_id"] = execution_id

    if save_result:
        experiments_dao.save_execution_test_data(result_dict=test_data,
                                                 filename=dir_name + "/" + test_data["test_id"])
