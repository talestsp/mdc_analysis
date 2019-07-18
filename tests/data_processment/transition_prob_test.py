import os
os.chdir("/home/tales/dev/master/mdc_analysis/")

import unittest
from src.ml.markov import transition_probabilities, distributive_transition_probabilities

class transition_prob_test(unittest.TestCase):

    def setUp(self):
        pass

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


