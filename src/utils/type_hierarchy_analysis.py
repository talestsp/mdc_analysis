import pandas as pd
import copy

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

def children(category, relations_freq):
    children_df = relations_freq[relations_freq["parent"] == category].sort_values("freq", ascending=False)
    children_df["prop"] = children_df["freq"] / children_df["freq"].sum()
    return children_df.sort_values("freq", ascending=False)

def parent(category, relations_freq):
    parent_df = copy.deepcopy(relations_freq[relations_freq["category"] == category])
    parent_df["prop"] = parent_df["freq"] / parent_df["freq"].sum()
    return parent_df.sort_values("freq", ascending=False)


def len_categs(categories):
    total = 0
    for key in categories.keys():
        total += len(categories[key])
    return total

def categ_relations(types):
    relations = []

    relations.append(("NULL", types[0]))

    for i in range(len(types) - 1):
        relation = (types[i], types[i + 1])
        relations.append(relation)

    relations.append((types[-1], "."))

    return relations

def relations_df(google_places_pois):
    relations = []

    for types in google_places_pois["types"]:
        for relation in categ_relations(types):
            row = {"category": relation[0], "parent": relation[1]}
            relations.append(row)

    return pd.DataFrame(relations)

def relations_freq(google_places_pois):
    relations_freq = relations_df(google_places_pois).groupby("parent")["category"].value_counts().to_frame().rename({'category': 'freq'},
                                                                                                 axis=1).reset_index().sort_values(
        "freq", ascending=False)
    return relations_freq