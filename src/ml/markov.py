import pandas as pd
import numpy as np

import src.exceptions.exceptions as exceptions


class MarkovChain(object):
    #MarkovChain class code from https://medium.com/@__amol__/markov-chains-with-python-1109663f3678
    def __init__(self, transition_prob):
        """
        Initialize the MarkovChain instance.

        Parameters
        ----------
        transition_prob: dict
            A dict object representing the transition
            probabilities in Markov Chain.
            Should be of the form:
                {'state1': {'state1': 0.1, 'state2': 0.4},
                 'state2': {...}}
        """
        self.transition_prob = transition_prob
        self.states = list(transition_prob.keys())

    def next_state(self, current_state):
        """
        Returns the state of the random variable at the next time
        instance.

        Parameters
        ----------
        current_state: str
            The current state of the system.
        """
        return np.random.choice(
            self.states,
            p=[self.transition_prob[current_state][next_state]
               for next_state in self.states]
        )

    def generate_states(self, current_state, no=10):
        """
        Generates the next states of the system.

        Parameters
        ----------
        current_state: str
            The state of the current random variable.

        no: int
            The number of future states to generate.
        """
        future_states = []
        for i in range(no):
            next_state = self.next_state(current_state)
            future_states.append(next_state)
            current_state = next_state
        return future_states

class MarkovPrediction:
    def __init__(self):
        self.markov_chain = None

    def fit(self, sequence_states):
        transition_probabilities = self.__transition_probabilities(sequence_states)
        self.markov_chain = MarkovChain(transition_prob=transition_probabilities)

        return self

    def get_markov_chain(self):
        if self.markov_chain is None:
            raise exceptions.ModelNotTrained()

    def next_state(self, current_state):
        return self.get_markov_chain().next_state(current_state)

    def generate_states(self, current_state, no=10):
        return self.get_markov_chain().generate_states(current_state, no=no)

    def __transition_probabilities(self, sequence_states, round_proba=4):
        trans_proba_df = pd.DataFrame()

        trans_proba_df["origin"] = sequence_states[0:-1]
        trans_proba_df["origin"] = trans_proba_df["origin"].astype(str)

        trans_proba_df["destination"] = sequence_states[1:]
        trans_proba_df["destination"] = trans_proba_df["destination"].astype(str)

        trans_proba_df["transition"] = trans_proba_df["origin"].astype(str) + " > " + trans_proba_df[
            "destination"].astype(str)
        trans_proba_df = trans_proba_df.set_index(trans_proba_df["transition"], drop=False)

        trans_freq_df = trans_proba_df["transition"].value_counts().to_frame()
        trans_freq_df = trans_freq_df.rename(index=str, columns={"transition": "transition_freq"})

        trans_proba_df = trans_proba_df.merge(trans_freq_df, left_index=True, right_index=True).reset_index(
            drop=True).drop_duplicates()
        del trans_proba_df["transition"]

        trans_proba_df["transition_freq"] = trans_proba_df["transition_freq"] / trans_proba_df["transition_freq"].sum()
        trans_proba_df["transition_freq"] = trans_proba_df["transition_freq"].round(round_proba)

        return trans_proba_df

    def __to_dict(self, trans_proba_df):
        # maybe using pandas pivot table improve time execution
        trans_proba_dict = {}
        trans_proba_df.apply(lambda row: self.__add_value(row, trans_proba_dict), axis=1)

        return trans_proba_dict

    def __add_value(self, row, trans_proba_dict):
        outter_key = row["origin"]
        inner_key = row["destination"]
        value = row["transition_freq"]

        if not outter_key in trans_proba_dict.keys():
            trans_proba_dict[outter_key] = {inner_key: value}
        else:
            trans_proba_dict[outter_key][inner_key] = value

        return trans_proba_dict