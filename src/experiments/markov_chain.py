import uuid
import src.ml.markov as mk
from src.utils.others import k_fold_iteration
from src.exceptions import exceptions
from src.dao import experiments_dao
from src.entity.stop_region import StopRegionGroup

def test_markov(train, test):
    trans_proba_dict = mk.to_dict(mk.transition_probabilities(train))
    predictor = mk.MarkovPredictor().fit(trans_proba_dict)

    states_trained_as_origin = []
    states_not_trained_as_origin = []
    hits = []
    misses = []

    for test_i in range(len(test[0:-1])):
        current_state = str(test[test_i])
        next_state_real = str(test[test_i + 1])

        try:
            next_state_pred = predictor.next_state(current_state)
            states_trained_as_origin.append(current_state)

        except exceptions.StateNotPresentInTrainAsOrigin:
            states_not_trained_as_origin.append(current_state)
            continue

        if next_state_real == next_state_pred:
            hits.append(next_state_real)
        else:
            misses.append({"real": next_state_real, "pred": next_state_pred})

    return {"total_hits": len(hits),
            "total_misses": len(misses),
            "hits": hits,
            "misses": misses,
            "total_states_trained_as_origin": len(states_trained_as_origin),
            "total_states_not_trained_as_origin": len(states_not_trained_as_origin),
            "states_trained_as_origin": states_trained_as_origin,
            "states_not_trained_as_origin": states_not_trained_as_origin}


def evaluation_markov_k_fold(sr_group, k=5, save_result=True):
    if sr_group.size() <= 1:
        print("sr_group size: {} \n skipping".format(sr_group.size()))
        raise exceptions.TooShortStopRegionGroup()

    tags_sequence = sr_group.sequence_stop_region_tags()["tag"].tolist()

    k_fold_partitions = k_fold_iteration(tags_sequence, k)

    execution_id = str(uuid.uuid4())

    for i in range(len(k_fold_partitions)):
        partition = k_fold_partitions[i]
        train = partition["train"]
        test = partition["test"]

        test_data = test_markov(train, test)
        test_data["trained_with"] = "same_user"
        test_data["train_size"] = len(train)
        test_data["test_size"] = len(test)
        test_data["method"] = "k_fold"
        test_data["k"] = k
        test_data["iteration"] = i
        test_data["user_id"] = sr_group.stop_region_list[0].user_id
        test_data["input_data_version"] = "markov-0.0"
        test_data["test_id"] = execution_id

        if save_result:
            experiments_dao.save_execution_test_data(result_dict=test_data, filename="markov_model/" + test_data["test_id"] + "_i_{}".format(i))


def all_users_vs_one(user_stop_region_group, save_result=True):
    for test_user in user_stop_region_group.keys():
        print(test_user)
        execution_id = str(uuid.uuid4())
        train_tags = []

        for train_user in user_stop_region_group.keys():
            sr_group = StopRegionGroup(user_stop_region_group[train_user], agglutinate_stop_regions=True)

            if train_user != test_user:
                train_tags = train_tags + sr_group.sequence_stop_region_tags()["tag"].tolist()

        sr_group_test = StopRegionGroup(user_stop_region_group[test_user], agglutinate_stop_regions=True)
        test_tags = sr_group_test.sequence_stop_region_tags()["tag"].tolist()

        test_data = test_markov(train_tags, test_tags)

        test_data["trained_with"] = "all_other_users"
        test_data["train_size"] = len(train_tags)
        test_data["test_size"] = len(test_tags)
        test_data["method"] = "all_users_vs_one"
        test_data["user_id"] = sr_group_test.stop_region_list[0].user_id
        test_data["input_data_version"] = "markov-0.0"
        test_data["test_id"] = execution_id

        if save_result:
            experiments_dao.save_execution_test_data(result_dict=test_data,
                                                     filename="markov_model/" + test_data["test_id"])
