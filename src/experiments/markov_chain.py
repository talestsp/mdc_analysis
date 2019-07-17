import uuid
import src.ml.markov as mk
from src.utils.others import k_fold_iteration
from src.exceptions import exceptions
from src.dao import experiments_dao


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

    for partition in k_fold_iteration(tags_sequence, k):
        train = partition["train"]
        test = partition["test"]

        test_data = test_markov(train, test)
        test_data["trained_with"] = "same_user"
        test_data["method"] = "k_fold"
        test_data["k"] = k
        test_data["user_id"] = sr_group.stop_region_list[0].user_id
        test_data["input_data_version"] = "markov-0.0"
        test_data["test_id"] = str(uuid.uuid4())

        if save_result:
            experiments_dao.save_execution_test_data(result_dict=test_data, filename=test_data["test_id"])
