import os
os.chdir("/home/tales/dev/master/mdc_analysis/")

import unittest
from src.utils.others import k_fold_iteration
import src.ml.markov as mk
from ast import literal_eval
from src.exceptions import exceptions

class markov_pred_test(unittest.TestCase):

    def setUp(self):
        self.tags_sequence = [['WORK'], ['cafe', 'food'], ['bus_station', 'transit_station'], ['lodging'],
                         ['bus_station', 'transit_station'], [], [], [], [], [], [], [], ['transit_station'],
                         ['clothing_store', 'store'], ['liquor_store', 'store'], ['WORK'], ['transit_station'],
                         ['school'], ['restaurant', 'food'], [], [], [], [], [], [], [], ['premise'], [], [], [], [],
                         [], [], [], [], ['WORK'], ['accounting', 'finance'], ['moving_company', 'storage'],
                         ['meal_takeaway', 'restaurant', 'food']]


    def test_prediction_not_distributive(self):
        for i in range(10):
            k_fold_partitions = k_fold_iteration(self.tags_sequence, k=5)

            for i in range(len(k_fold_partitions)):
                partition = k_fold_partitions[i]
                train = partition["train"]
                test = partition["test"]

                trans_proba_dict = mk.to_dict(mk.transition_probabilities(train))

                predictor = mk.MarkovPredictor().fit(trans_proba_dict)

                print("markov states")
                print(predictor.get_states())

                for test_i in range(len(test[0:-1])):
                    current_state_list = test[test_i]
                    next_state_real_list = test[test_i + 1]

                    if not is_valid_state(current_state_list) or not is_valid_state(next_state_real_list):
                        continue

                    current_state = str(current_state_list)

                    try:
                        next_state_pred_list = literal_eval(predictor.next_state(current_state))

                    except exceptions.StateNotPresentInTrainAsOrigin:
                        continue

                    print()
                    print("curr", current_state_list, type(current_state_list))
                    print("real", next_state_real_list, type(next_state_real_list))
                    print("pred", next_state_pred_list, type(next_state_pred_list))
                    print(set(next_state_real_list) == set(next_state_pred_list))

                    self.assertNotIn([], next_state_pred_list)
                    self.assertNotIn("[]", next_state_pred_list)

                    self.assertNotEqual([], next_state_pred_list)
                    self.assertNotEqual("[]", next_state_pred_list)


    def test_prediction_distributive(self):
        for i in range(10):
            k_fold_partitions = k_fold_iteration(self.tags_sequence, k=5)

            for i in range(len(k_fold_partitions)):
                partition = k_fold_partitions[i]
                train = partition["train"]
                test = partition["test"]

                trans_proba_dict = mk.to_dict(mk.distributive_transition_probabilities(train))

                predictor = mk.MarkovPredictor().fit(trans_proba_dict)

                for test_i in range(len(test[0:-1])):
                    current_state_list = test[test_i]
                    next_state_real_list = test[test_i + 1]

                    if not is_valid_state(current_state_list) or not is_valid_state(next_state_real_list):
                        continue

                    current_state = str(current_state_list)

                    next_state_pred_list = []
                    for state in literal_eval(current_state):
                        print("state:", state)
                        try:
                            next_state = predictor.next_state(state)
                            print("next_state:", next_state)
                            next_state_pred_list.append(next_state)

                        except exceptions.StateNotPresentInTrainAsOrigin:
                            print("state <{}> not present in training".format(state))
                            continue
                    print("-----")
                    print("curr", current_state_list, type(current_state_list))
                    print("real", next_state_real_list, type(next_state_real_list))
                    print("pred", next_state_pred_list, type(next_state_pred_list))
                    print(set(next_state_real_list) == set(next_state_pred_list))

                    self.assertNotIn([], next_state_pred_list)
                    self.assertNotIn("[]", next_state_pred_list)

                    self.assertNotEqual([], next_state_pred_list)
                    self.assertNotEqual("[]", next_state_pred_list)






def is_valid_state(state):
    if state == "[]" or state == []:
        return False
    else:
        return True