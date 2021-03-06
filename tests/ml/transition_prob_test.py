import os
os.chdir("/home/tales/dev/master/mdc_analysis/")

import ast
import pandas as pd

import unittest
from src.ml.markov import transition_probabilities, distributive_transition_probabilities, equalize_transition_prob, cluster_transition_probabilities

class transition_prob_test(unittest.TestCase):

    def setUp(self):
        self.agg_6074_0_tags = [['WORK'], ['cafe', 'food'], ['bus_station', 'transit_station'], ['lodging'],
                         ['bus_station', 'transit_station'], [], [], [], [], [], [], [], ['transit_station'],
                         ['clothing_store', 'store'], ['liquor_store', 'store'], ['WORK'], ['transit_station'],
                         ['school'], ['restaurant', 'food'], [], [], [], [], [], [], [], ['premise'], [], [], [], [],
                         [], [], [], [], ['WORK'], ['accounting', 'finance'], ['moving_company', 'storage'],
                         ['meal_takeaway', 'restaurant', 'food']]

    def test_transition_prob_df(self):
        sequence = ["A", "B", "A", "C", "A", "D", "B", "C", "B", "C", "A", "Z", "B", "C", "B", "C"]

        trans_proba = transition_probabilities(sequence)

        self.assertEqual(1, trans_proba[trans_proba["origin"] == "A"]["transition_freq"].sum())
        self.assertEqual(1, trans_proba[trans_proba["origin"] == "B"]["transition_freq"].sum())
        self.assertEqual(1, trans_proba[trans_proba["origin"] == "C"]["transition_freq"].sum())

        self.assertEqual(0.25, trans_proba[(trans_proba["origin"] == "A") & (trans_proba["destination"] == "B")][
            "transition_freq"].item())
        self.assertEqual(0.8, trans_proba[(trans_proba["origin"] == "B") & (trans_proba["destination"] == "C")][
            "transition_freq"].item())

    # def test_transition_equal_proba(self):
    #     sequence = ["A", "B", "A", "C", "A", "D", "B", "C", "B", "C", "A", "Z", "B", "C", "B", "C", "X", "C", "A"]
    #
    #     trans_proba = transition_probabilities_equal(sequence)
    #
    #     for origin in trans_proba["origin"]:
    #         print("origin:", origin)
    #         origin_df = trans_proba[trans_proba["origin"] == origin]
    #
    #         for transition_freq in origin_df["transition_freq"]:
    #             self.assertAlmostEqual(origin_df["transition_freq"].mean(), transition_freq, delta=0.01)


    def test_equalize_transition_prob(self):
        sequence = ["A", "B", "A", "C", "A", "D", "B", "C", "B", "C", "A", "Z", "B", "C", "B", "C", "J", "A", "T", "A", "S"]

        trans_proba = equalize_transition_prob(transition_probabilities(sequence))

        for origin in trans_proba["origin"]:
            origin_df = trans_proba[trans_proba["origin"] == origin]

            for transition_freq in origin_df["transition_freq"]:
                self.assertAlmostEqual(origin_df["transition_freq"].mean(), transition_freq, delta=0.01)


        self.assertAlmostEqual(0.16667, trans_proba[trans_proba["origin"] == "A"]["transition_freq"].mean(), delta=0.001)

    def test_distributive_transition_prob_df(self):
        sequence = [["A"], ["B"], ["X", "Y", "Z"], "B", "Y", "B"]

        trans_proba = distributive_transition_probabilities(sequence)

        self.assertEqual(1, trans_proba[trans_proba["origin"] == "A"]["transition_freq"].sum())
        self.assertEqual(1, trans_proba[trans_proba["origin"] == "B"]["transition_freq"].sum())
        self.assertEqual(1, trans_proba[trans_proba["origin"] == "X"]["transition_freq"].sum())
        self.assertEqual(1, trans_proba[trans_proba["origin"] == "Y"]["transition_freq"].sum())
        self.assertEqual(1, trans_proba[trans_proba["origin"] == "Z"]["transition_freq"].sum())

        self.assertEqual(0.5, trans_proba[(trans_proba["origin"] == "B") & (trans_proba["destination"] == "Y")][
            "transition_freq"].item())
        self.assertEqual(1, trans_proba[(trans_proba["origin"] == "Y") & (trans_proba["destination"] == "B")][
            "transition_freq"].item())

    def test_tag_type(self):
        dist_trans_proba = distributive_transition_probabilities(self.agg_6074_0_tags)
        trans_proba = transition_probabilities(self.agg_6074_0_tags)

        for tags in trans_proba["origin"].tolist():
            self.assertEqual(type(tags), str)

        for tags in dist_trans_proba["origin"].tolist():
            self.assertEqual(type(tags), str)

    def test_clean_data(self):
        dist_trans_proba = distributive_transition_probabilities(self.agg_6074_0_tags)
        trans_proba = transition_probabilities(self.agg_6074_0_tags)

        self.assertNotIn([], trans_proba["origin"].tolist())
        self.assertNotIn("[]", trans_proba["origin"])
        self.assertNotIn([], dist_trans_proba["origin"].tolist())
        self.assertNotIn("[]", dist_trans_proba["origin"])

        self.assertNotIn([], trans_proba["destination"].tolist())
        self.assertNotIn("[]", trans_proba["destination"])
        self.assertNotIn([], dist_trans_proba["destination"].tolist())
        self.assertNotIn("[]", dist_trans_proba["destination"])

    def test_transitions_origins_and_destinations(self):
        dist_trans_proba = distributive_transition_probabilities(self.agg_6074_0_tags)
        trans_proba = transition_probabilities(self.agg_6074_0_tags)

        tags_origin = ["['WORK']", "['cafe', 'food']", "['bus_station', 'transit_station']", "['lodging']",
         "['transit_station']", "['clothing_store', 'store']", "['liquor_store', 'store']", "['school']",
         "['accounting', 'finance']", "['moving_company', 'storage']", "['meal_takeaway', 'restaurant', 'food']"]

        tags_destination = ["['WORK']", "['cafe', 'food']", "['bus_station', 'transit_station']", "['lodging']",
         "['transit_station']", "['clothing_store', 'store']", "['liquor_store', 'store']", "['school']",
         "['restaurant', 'food']", "['accounting', 'finance']", "['moving_company', 'storage']",
         "['meal_takeaway', 'restaurant', 'food']"]

        for tags in tags_origin[:-1]:
            self.assertIn(tags, trans_proba["origin"].tolist())

            for tag in ast.literal_eval(tags):
                self.assertIn(tag, dist_trans_proba["origin"].tolist())

        for tags in tags_destination[1:]:
            self.assertIn(tags, trans_proba["destination"].tolist())

            for tag in ast.literal_eval(tags):
                self.assertIn(tag, dist_trans_proba["destination"].tolist())


    def test_transitions_origins_and_destinations(self):
        tags_1 = ["A", "B", "A", "C", "A", "D"]
        tags_2 = ["A", "X", "A", "C", "A", "D", "X"]
        tags_3 = ["A", "Y", "A", "Y", "C", "A", "D", "Y"]

        cluster_transitions = pd.DataFrame()

        for tags in [tags_1, tags_2, tags_3]:
            transitions = transition_probabilities(tags)
            cluster_transitions = cluster_transitions.append(transitions)

        cluster_transitions = cluster_transitions.groupby(["origin", "destination"])["transition_count"].sum().to_frame().reset_index()

        self.assertEquals(cluster_transitions[(cluster_transitions["origin"] == "A") &
                                              (cluster_transitions["destination"] == "D")]["transition_count"].item(),3)

        self.assertEquals(cluster_transitions[(cluster_transitions["origin"] == "C") &
                                              (cluster_transitions["destination"] == "A")]["transition_count"].item(),3)

        self.assertEquals(cluster_transitions[(cluster_transitions["origin"] == "X") &
                                              (cluster_transitions["destination"] == "A")]["transition_count"].item(),1)

        self.assertEquals(cluster_transitions[(cluster_transitions["origin"] == "Y") &
                                              (cluster_transitions["destination"] == "A")]["transition_count"].item(),1)

        self.assertEquals(len(cluster_transitions[(cluster_transitions["origin"] == "D") &
                                              (cluster_transitions["destination"] == "A")]),0)



        cluster_transitions = cluster_transition_probabilities([tags_1, tags_2, tags_3])

        self.assertEquals(cluster_transitions[(cluster_transitions["origin"] == "A") &
                                              (cluster_transitions["destination"] == "D")]["transition_count"].item(),3)

        self.assertEquals(cluster_transitions[(cluster_transitions["origin"] == "C") &
                                              (cluster_transitions["destination"] == "A")]["transition_count"].item(),3)

        self.assertEquals(cluster_transitions[(cluster_transitions["origin"] == "X") &
                                              (cluster_transitions["destination"] == "A")]["transition_count"].item(),1)

        self.assertEquals(cluster_transitions[(cluster_transitions["origin"] == "Y") &
                                              (cluster_transitions["destination"] == "A")]["transition_count"].item(),1)

        self.assertEquals(len(cluster_transitions[(cluster_transitions["origin"] == "D") &
                                              (cluster_transitions["destination"] == "A")]),0)

        self.assertAlmostEqual(cluster_transitions[(cluster_transitions["origin"] == "A") &
                                                  (cluster_transitions["destination"] == "B")]["transition_freq"].item(), 1/9)
