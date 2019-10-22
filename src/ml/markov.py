import pandas as pd
import numpy as np
import src.exceptions.exceptions as exceptions



class MarkovPredictor:
    def __init__(self):
        self.markov_chain = None

    def fit(self, transition_probabilities_dict):
        self.markov_chain = MarkovChain(transition_prob=transition_probabilities_dict)

        return self

    def get_markov_chain(self):
        if self.markov_chain is None:
            raise exceptions.ModelNotTrained()
        return self.markov_chain

    def next_state(self, current_state):
        try:
            return self.get_markov_chain().next_state(current_state)
        except KeyError:
            raise exceptions.StateNotPresentInTrainAsOrigin()


    def generate_states(self, current_state, no=10):
        return self.get_markov_chain().generate_states(current_state, no=no)

    def get_states(self):
        return self.get_markov_chain().states

def to_dict(trans_proba_df):
    # maybe using pandas pivot table improve time execution
    trans_proba_dict = {}
    trans_proba_df.apply(lambda row: __add_value(row, trans_proba_dict), axis=1)

    return trans_proba_dict

def __add_value(row, trans_proba_dict):
    outter_key = row["origin"]
    inner_key = row["destination"]
    value = row["transition_freq"]

    if not outter_key in trans_proba_dict.keys():
        trans_proba_dict[outter_key] = {inner_key: value}
    else:
        trans_proba_dict[outter_key][inner_key] = value

    return trans_proba_dict

def transition_probabilities(sequence_states):
    trans_proba_df = pd.DataFrame()

    if type(sequence_states) is pd.Series:
        sequence_states = sequence_states.tolist()

    trans_proba_df["origin"] = sequence_states[0:-1]
    trans_proba_df["origin"] = trans_proba_df["origin"].astype(str)

    trans_proba_df["destination"] = sequence_states[1:]
    trans_proba_df["destination"] = trans_proba_df["destination"].astype(str)

    return calculate_proba_per_origin(trans_proba_df)[["origin", "destination", "transition_freq", "transition_count"]]

def cluster_transition_probabilities(list_of_tags):
    cluster_transitions = pd.DataFrame()

    for tags in list_of_tags:
        transitions = transition_probabilities(tags)
        cluster_transitions = cluster_transitions.append(transitions)

    return cluster_transitions.groupby(["origin", "destination"])["transition_count"].sum().to_frame().reset_index()

def transition_probabilities_equal(sequence_states):
    trans_proba_df = pd.DataFrame()

    if type(sequence_states) is pd.Series:
        sequence_states = sequence_states.tolist()

    trans_proba_df["origin"] = sequence_states[0:-1]
    trans_proba_df["origin"] = trans_proba_df["origin"].astype(str)

    trans_proba_df["destination"] = sequence_states[1:]
    trans_proba_df["destination"] = trans_proba_df["destination"].astype(str)

    same_proba = trans_proba_df.groupby("origin").apply(lambda group: 1 / len(group))

    trans_proba_df = trans_proba_df.merge(same_proba.to_frame(), how='left', left_on="origin", right_index=True).rename(
        columns={0: "transition_freq"})

    return trans_proba_df

def equalize_transition_prob(trans_proba_df):
    del trans_proba_df["transition_freq"]

    same_proba = trans_proba_df.groupby("origin").apply(lambda group: 1 / len(group))

    trans_proba_df = trans_proba_df.merge(same_proba.to_frame(), how='left', left_on="origin", right_index=True).rename(
        columns={0: "transition_freq"})

    return trans_proba_df


def distributive_transition_probabilities(tags_sequence):
    transitions = []

    last_tags = tags_sequence[0]
    for tags in tags_sequence[1:]:
        tags = list(set(tags))

        for origin_tag in last_tags:
            for destination_tag in tags:
                transitions.append({"origin": origin_tag, "destination": destination_tag})

        last_tags = tags

    transition_df = pd.DataFrame(transitions)[["origin", "destination"]]
    transition_df["origin"] = transition_df["origin"].astype(str)
    transition_df["destination"] = transition_df["destination"].astype(str)

    return calculate_proba_per_origin(transition_df)[["origin", "destination", "transition_freq"]]

def calculate_proba_per_origin(transitions_df):
    transitions_df = remove_transitions_with_empty_tags(transitions_df)

    transitions_df["transition"] = transitions_df["origin"].astype(str) + " > " + transitions_df[
        "destination"].astype(str)
    trans_proba_df = transitions_df.set_index(transitions_df["transition"], drop=False)

    trans_freq_df = trans_proba_df["transition"].value_counts().to_frame()

    trans_freq_df = trans_freq_df.rename(index=str, columns={"transition": "transition_count"})

    trans_proba_df = trans_proba_df.merge(trans_freq_df, left_index=True, right_index=True).reset_index(
        drop=True).drop_duplicates()
    del trans_proba_df["transition"]

    freq_grouped_by_origin = trans_proba_df.groupby("origin").apply(lambda group: group["transition_count"] / group["transition_count"].sum())

    #del trans_proba_df["transition_freq"]
    del trans_proba_df["origin"]

    try:
        freq_grouped_by_origin = freq_grouped_by_origin.to_frame()
    except AttributeError:
        freq_grouped_by_origin_dict = freq_grouped_by_origin.to_dict()

        print(freq_grouped_by_origin_dict)
        index = list(freq_grouped_by_origin_dict.keys())[0]
        origin_value = list(freq_grouped_by_origin_dict[index].keys())[0]
        transition_freq_value = freq_grouped_by_origin_dict[index][list(freq_grouped_by_origin_dict[index].keys())[0]]

        freq_grouped_by_origin = pd.DataFrame.from_dict({"transition_count": {(origin_value, index): transition_freq_value}})

        freq_grouped_by_origin = freq_grouped_by_origin.set_index(freq_grouped_by_origin.index.rename(['origin', None]))


    freq_grouped_by_origin = freq_grouped_by_origin.rename(columns={"transition_count": "transition_freq"})
    trans_proba_df = freq_grouped_by_origin.reset_index().merge(trans_proba_df.reset_index(), how="inner",
                                                                           left_on="level_1", right_on="index")


    del trans_proba_df["index"]
    del trans_proba_df["level_1"]

    return trans_proba_df[["origin", "destination", "transition_freq", "transition_count"]]

def remove_transitions_with_empty_tags(transitions):
    return transitions[(transitions["origin"].astype(str) != "[]") & (transitions["destination"].astype(str) != "[]")]

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
            list(self.transition_prob[current_state].keys()),
            p=[self.transition_prob[current_state][next_state]
               for next_state in self.transition_prob[current_state].keys()]
        )

    def next_state_deprecated(self, current_state):
        """
        Returns the state of the random variable at the next time
        instance.

        Parameters
        ----------
        current_state: str
            The current state of the system.
        """

        raise Exception("THIS METHOD IS DEPRECATED BECAUSE IT NEED A COMPLETE GRAPH OF STATES")

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


