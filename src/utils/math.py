import pandas as pd
from src.exceptions import exceptions

def normalize(col_series, complement=False):
    if complement:
        return 1 - ((col_series - col_series.min()) / (col_series.max() - col_series.min()))
    else:
        return (col_series - col_series.min()) / (col_series.max() - col_series.min())


def fill_prob_1(values, tolerance=0.000001):
    '''
    Fills probabilities list to 1
    :param values:
    :param tolerance: Difference from probabilities sum to 1 must be under this tolerance value
    :return:
    '''
    if not type(values) is pd.Series():
        values = pd.Series(values)

    diff = 1 - values.sum()

    if abs(diff) > tolerance:
        raise exceptions.ValueFarFromOne()

    print("diff:", diff)

    random_value = values.sample()
    random_index = random_value.index.item()

    values.update(pd.Series([random_value + diff], index=[random_index]))

    return values.tolist()

