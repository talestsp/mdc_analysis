import pandas as pd

def term_list_index(term, lista):
    if term in lista:
        return lista.index(term)
    else:
        return -1


def term_index_len(term, types_series):
    term_index = types_series.apply(lambda lista: term_list_index(term, lista))
    term_types_len = types_series.apply(lambda lista: len(lista))

    return pd.DataFrame({"index": term_index, "len": term_types_len})


def left_right_term(term, types_series):
    lefts = []
    rights = []

    term_index_len_df = term_index_len(term, types_series)

    for type_row in types_series.loc[term_index_len_df[term_index_len_df["index"] >= 0].index]:
        left = type_row[0:type_row.index(term)]
        lefts = lefts + left
        right = type_row[type_row.index(term) + 1:]
        rights = rights + right

    lefts = pd.Series(lefts).rename({0: "left"})
    rights = pd.Series(rights).rename({0: "right"})

    lr = lefts.value_counts().to_frame().merge(rights.value_counts().to_frame(), how="outer",
                                               left_index=True,
                                               right_index=True)

    return lr.sort_values(by=["0_x", "0_y"], ascending=False).rename({"0_x": "left", "0_y": "right"}, axis=1)


def term_placement_analisis(lr, show=True):
    '''
    Return 3 pandas.DataFrame.
    One for elements that happen at any position left.
    One for elements that happen at any position right.
    One for elements that happen at any position in both sides.
    :param lr:
    :param show:
    :return:
    '''
    right = lr[(lr["left"].isna()) & (~lr["right"].isna())]
    left = lr[(lr["right"].isna()) & (~lr["left"].isna())]
    both_valid = lr[~(lr["right"].isna()) & (~lr["left"].isna())]

    if show:
        print("RIGHT side occurrences")
        print()
        print(right)
        print("---")
        print()
        print("LEFT side occurrences")
        print(left)
        print("---")
        print()
        print("BOTH sides occurrences")
        print(both_valid)
        print("---")
        print()
    return {"right": right, "left": left, "both": both_valid}