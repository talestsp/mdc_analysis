import os
os.chdir("/home/tales/dev/master/mdc_analysis/")

import unittest
import pandas as pd

from src.utils.others import k_fold_iteration
from src.experiments.ctw_eval import test_ctw

class markov_pred_test(unittest.TestCase):

    def setUp(self):
        self.tags_sequence_6087 = ['HOME', 'NoCategoryMatched', 'lawyer', 'political', 'NoCategoryMatched', 'HOME',
                                   'hair_care', 'health', 'hair_care', 'HOME', 'convenience_store', 'HOME',
                                   'NoCategoryMatched', 'school', 'NoCategoryMatched', 'store', 'NoCategoryMatched',
                                   'local_government_office', 'NoCategoryMatched', 'HOME', 'NoCategoryMatched',
                                   'transit_station', 'NoCategoryMatched', 'transit_station', 'NoCategoryMatched',
                                   'store', 'finance', 'NoCategoryMatched', 'health', 'cafe', 'NoCategoryMatched',
                                   'transit_station', 'NoCategoryMatched', 'transit_station', 'NoCategoryMatched',
                                   'store', 'NoCategoryMatched', 'NoCategoryMatched', 'NoCategoryMatched',
                                   'transit_station', 'NoCategoryMatched', 'political', 'NoCategoryMatched',
                                   'transit_station', 'NoCategoryMatched', 'transit_station', 'NoCategoryMatched',
                                   'health', 'NoCategoryMatched', 'transit_station', 'NoCategoryMatched',
                                   'transit_station', 'NoCategoryMatched', 'hair_care', 'transit_station',
                                   'NoCategoryMatched', 'finance', 'general_contractor', 'NoCategoryMatched', 'health',
                                   'NoCategoryMatched', 'travel_agency', 'NoCategoryMatched', 'NoCategoryMatched',
                                   'supermarket', 'NoCategoryMatched', 'NoCategoryMatched', 'transit_station',
                                   'NoCategoryMatched', 'restaurant', 'store', 'convenience_store', 'health',
                                   'lodging', 'store', 'transit_station', 'NoCategoryMatched', 'NoCategoryMatched',
                                   'cafe', 'NoCategoryMatched', 'transit_station', 'NoCategoryMatched',
                                   'local_government_office', 'NoCategoryMatched', 'bar', 'NoCategoryMatched',
                                   'school', 'NoCategoryMatched', 'transit_station', 'NoCategoryMatched',
                                   'NoCategoryMatched', 'restaurant', 'restaurant', 'restaurant', 'transit_station',
                                   'NoCategoryMatched', 'store', 'finance', 'restaurant', 'restaurant',
                                   'NoCategoryMatched', 'restaurant', 'NoCategoryMatched', 'liquor_store', 'store',
                                   'real_estate_agency', 'NoCategoryMatched', 'beauty_salon', 'NoCategoryMatched',
                                   'transit_station', 'NoCategoryMatched', 'health', 'NoCategoryMatched',
                                   'transit_station', 'lodging', 'restaurant', 'transit_station', 'finance',
                                   'transit_station', 'NoCategoryMatched', 'lodging', 'NoCategoryMatched', 'hair_care',
                                   'NoCategoryMatched', 'hair_care', 'convenience_store', 'NoCategoryMatched', 'cafe',
                                   'NoCategoryMatched', 'cafe', 'transit_station', 'NoCategoryMatched', 'store',
                                   'NoCategoryMatched', 'political', 'NoCategoryMatched', 'hair_care', 'hair_care',
                                   'NoCategoryMatched', 'cafe', 'hair_care', 'NoCategoryMatched', 'place_of_worship',
                                   'NoCategoryMatched', 'place_of_worship', 'NoCategoryMatched', 'transit_station',
                                   'NoCategoryMatched', 'store', 'transit_station', 'travel_agency', 'restaurant',
                                   'restaurant', 'restaurant', 'transit_station', 'bakery', 'place_of_worship',
                                   'political', 'lodging', 'transit_station', 'NoCategoryMatched', 'place_of_worship',
                                   'transit_station', 'NoCategoryMatched', 'general_contractor', 'cafe',
                                   'transit_station', 'NoCategoryMatched', 'transit_station', 'NoCategoryMatched',
                                   'NoCategoryMatched', 'NoCategoryMatched', 'NoCategoryMatched', 'transit_station',
                                   'cafe', 'school', 'cafe', 'school', 'cafe', 'transit_station', 'NoCategoryMatched',
                                   'store', 'place_of_worship', 'NoCategoryMatched', 'transit_station',
                                   'NoCategoryMatched', 'place_of_worship', 'NoCategoryMatched', 'place_of_worship',
                                   'cafe', 'NoCategoryMatched', 'store', 'lodging', 'lodging', 'NoCategoryMatched',
                                   'store', 'place_of_worship', 'place_of_worship', 'NoCategoryMatched',
                                   'NoCategoryMatched', 'transit_station', 'NoCategoryMatched', 'restaurant',
                                   'NoCategoryMatched', 'place_of_worship', 'NoCategoryMatched', 'cafe',
                                   'NoCategoryMatched', 'transit_station', 'NoCategoryMatched', 'general_contractor',
                                   'store', 'health', 'transit_station', 'NoCategoryMatched', 'store',
                                   'NoCategoryMatched', 'bar', 'store', 'NoCategoryMatched', 'transit_station',
                                   'NoCategoryMatched', 'NoCategoryMatched', 'NoCategoryMatched', 'NoCategoryMatched',
                                   'NoCategoryMatched', 'NoCategoryMatched', 'store', 'NoCategoryMatched',
                                   'NoCategoryMatched', 'place_of_worship', 'cafe', 'NoCategoryMatched', 'health',
                                   'NoCategoryMatched', 'NoCategoryMatched', 'NoCategoryMatched', 'store',
                                   'NoCategoryMatched', 'finance', 'store', 'NoCategoryMatched', 'health', 'health',
                                   'NoCategoryMatched', 'hair_care', 'NoCategoryMatched', 'beauty_salon', 'finance',
                                   'bar', 'cafe', 'NoCategoryMatched', 'cafe', 'NoCategoryMatched', 'restaurant',
                                   'NoCategoryMatched', 'health', 'restaurant', 'beauty_salon', 'transit_station',
                                   'NoCategoryMatched', 'restaurant']

        self.tags_sequence_6189 = ['transit_station', 'HOME', 'health', 'transit_station', 'finance', 'health', 'health', 'NoCategoryMatched', 'bakery', 'HOME', 'political', 'WORK', 'health', 'WORK', 'health', 'health', 'transit_station', 'cafe', 'real_estate_agency', 'WORK', 'political', 'finance', 'NoCategoryMatched', 'restaurant', 'restaurant', 'health', 'HOME', 'health', 'store', 'grocery_or_supermarket', 'HOME', 'store', 'HOME', 'political', 'convenience_store', 'cafe', 'health', 'WORK', 'store', 'HOME', 'store', 'store', 'store', 'cafe', 'WORK', 'WORK', 'restaurant', 'store', 'health', 'store', 'convenience_store', 'cafe', 'HOME', 'political', 'store', 'transit_station', 'WORK', 'cafe', 'store', 'store', 'health', 'health', 'beauty_salon', 'WORK', 'health', 'restaurant', 'WORK', 'HOME', 'WORK', 'political', 'restaurant', 'political', 'travel_agency', 'restaurant', 'general_contractor', 'store', 'HOME', 'real_estate_agency', 'place_of_worship', 'store', 'store', 'store', 'health', 'restaurant', 'HOME', 'health', 'store', 'store', 'store', 'store', 'store', 'transit_station', 'NoCategoryMatched', 'health', 'health', 'cafe', 'HOME', 'store', 'store', 'store', 'WORK', 'HOME', 'restaurant', 'general_contractor', 'HOME', 'general_contractor', 'health', 'HOME', 'hair_care', 'political', 'NoCategoryMatched', 'store', 'NoCategoryMatched', 'HOME', 'cafe', 'store', 'HOME', 'WORK', 'store', 'health', 'WORK', 'HOME', 'political', 'political', 'HOME', 'lodging', 'WORK', 'restaurant', 'HOME', 'lodging', 'WORK', 'store', 'health', 'store', 'HOME', 'bar', 'store', 'health', 'supermarket', 'store', 'store', 'store', 'store', 'health', 'general_contractor', 'health', 'general_contractor', 'HOME', 'WORK', 'cafe', 'convenience_store', 'political', 'health', 'WORK', 'store', 'HOME', 'school', 'HOME', 'health', 'cafe', 'restaurant', 'HOME', 'cafe', 'store', 'store', 'cafe', 'restaurant', 'real_estate_agency', 'health', 'WORK', 'health', 'WORK', 'finance', 'health', 'NoCategoryMatched', 'restaurant', 'HOME', 'WORK', 'political', 'real_estate_agency', 'convenience_store', 'hair_care', 'WORK', 'health', 'WORK', 'HOME', 'health', 'WORK', 'finance', 'WORK', 'restaurant', 'restaurant', 'store', 'HOME', 'convenience_store', 'real_estate_agency', 'political', 'convenience_store', 'general_contractor', 'NoCategoryMatched', 'convenience_store', 'restaurant', 'store', 'HOME', 'political', 'HOME', 'transit_station', 'cafe', 'store', 'health', 'convenience_store', 'store', 'HOME', 'WORK', 'NoCategoryMatched', 'store', 'transit_station', 'store', 'health', 'NoCategoryMatched', 'school', 'HOME', 'convenience_store', 'WORK', 'health', 'health', 'health', 'health', 'WORK', 'store', 'HOME', 'restaurant', 'convenience_store', 'store', 'cafe', 'health', 'WORK', 'restaurant', 'HOME', 'health', 'HOME', 'health', 'HOME', 'political', 'HOME', 'WORK', 'finance', 'HOME', 'WORK', 'store', 'transit_station', 'NoCategoryMatched', 'health', 'HOME', 'health', 'HOME', 'health', 'transit_station', 'hair_care', 'convenience_store', 'finance', 'grocery_or_supermarket', 'health', 'political', 'WORK', 'convenience_store', 'HOME', 'political', 'WORK', 'restaurant', 'finance', 'school', 'convenience_store', 'HOME', 'store', 'store', 'store', 'HOME', 'WORK', 'store', 'health', 'finance', 'political', 'transit_station', 'WORK', 'lodging', 'cafe', 'store', 'hair_care', 'store', 'health', 'restaurant', 'health', 'HOME', 'store', 'HOME', 'WORK', 'WORK', 'restaurant', 'restaurant', 'HOME', 'convenience_store', 'WORK', 'health', 'beauty_salon', 'HOME', 'general_contractor', 'convenience_store', 'HOME', 'hair_care', 'store', 'HOME', 'school', 'health', 'transit_station', 'convenience_store', 'real_estate_agency', 'health', 'health', 'health', 'political', 'convenience_store', 'transit_station', 'store', 'store', 'HOME', 'political', 'store', 'travel_agency', 'political', 'NoCategoryMatched', 'transit_station', 'transit_station', 'HOME', 'store', 'WORK', 'HOME', 'political', 'health', 'general_contractor', 'political', 'HOME', 'store', 'HOME', 'store', 'HOME', 'store', 'restaurant', 'general_contractor', 'store', 'HOME', 'beauty_salon', 'WORK', 'health', 'transit_station', 'health', 'bar', 'political', 'beauty_salon', 'NoCategoryMatched', 'WORK', 'hair_care', 'convenience_store', 'convenience_store', 'real_estate_agency', 'store', 'political', 'HOME', 'store', 'restaurant', 'hair_care', 'liquor_store', 'hair_care', 'bakery', 'HOME', 'school', 'health', 'transit_station', 'HOME', 'political', 'political', 'NoCategoryMatched', 'HOME', 'health', 'finance', 'real_estate_agency', 'political', 'WORK', 'hair_care', 'finance', 'hair_care', 'school', 'WORK', 'hair_care', 'lodging', 'HOME', 'political', 'lodging', 'NoCategoryMatched', 'WORK', 'store', 'beauty_salon', 'store']


    def test_test_emelent_not_in_train(self):

        tags_map = {"6189": self.tags_sequence_6189, "6087": self.tags_sequence_6087}

        for key in tags_map.keys():
            print()
            print("=======================")
            print("USER:", key)
            print()
            k_fold_partitions = k_fold_iteration(tags_map[key], 4)

            for i in range(len(k_fold_partitions)):
                partition = k_fold_partitions[i]
                train = partition["train"]
                test = partition["test"]

                dep_train = pd.DataFrame({"p1": train[:-1], "p2": train[1:]})
                dep_train["trans_2"] = dep_train["p1"] + " + " + dep_train["p2"]

                dep_test = pd.DataFrame({"p1": test[:-1], "p2": test[1:]})
                dep_test["trans_2"] = dep_test["p1"] + " + " + dep_test["p2"]

                print(dep_test["trans_2"].apply(lambda value : value in dep_train["trans_2"].tolist()).value_counts())

                test_data = test_ctw(train, test, depth=3, predict_choice_method="most_likely")

                print("len(test)", len(test))
                print("len(train)", len(train))
                print()


        kkkk