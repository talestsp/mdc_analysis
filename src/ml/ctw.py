import pandas as pd
import numpy as np
import random
from src.ml.context_tree_weighting.ctw import CTW

class MyCTW:

    def __init__(self, depth, symbols, sidesymbols=None):
        if sidesymbols is None:
            self.ctw = CTW(depth=depth, symbols=symbols)
        else:
            self.ctw = CTW(depth=depth, symbols=symbols, sidesymbols=sidesymbols)

    def prediction_proba(self, seq, sideseq=None):
        print("seq")
        print(seq)
        print("sideseq")
        print(sideseq)
        print()

        if sideseq is None:
            return self.ctw.predict_sequence(seq=seq)
        else:
            return self.ctw.predict_sequence(seq=seq, sideseq=sideseq)

    def prediction(self, seq, sideseq=None, method="most_likely"):
        '''

        :param pred_proba:
        :param method: either "most_likely" or "random_choice" or "random_dummy"
        :return:
        '''

        mapped_tags, tags_map = self._tag_to_numeric(seq)

        pred_proba = self.prediction_proba(mapped_tags, sideseq)

        if method == "most_likely":
            pred = pd.DataFrame(pred_proba).apply(lambda column: column.sample(len(column)).idxmax(), axis=0)

        elif method == "random_choice":
            pred = pd.DataFrame(pred_proba).apply(
                lambda column: np.random.choice(a=column.index.tolist(), p=column.tolist()))

        elif method == "random_dummy":
            pred = pd.DataFrame(pred_proba).apply(lambda column: column.loc[random.randint(column.index.min(), column.index.max())], axis=0)

        return self._numeric_back_to_tag(pred, tags_map)

    def _tag_to_numeric(self, sequence):
        tag_map = pd.Series(sequence).drop_duplicates().reset_index(drop=True).reset_index().set_index(0).to_dict()[
            "index"]
        mapped_sequence = pd.Series(sequence).replace(tag_map)
        return mapped_sequence, tag_map

    def _reverse_map(self, a_map):
        reversed_map = {}
        for key in a_map:
            reversed_map[a_map[key]] = key
        return reversed_map

    def _numeric_back_to_tag(self, numeric_sequence, tags_map):
        tags_sequence = []
        reversed_map = self._reverse_map(tags_map)

        for num in numeric_sequence:
            tags_sequence.append(reversed_map[num])

        return tags_sequence
