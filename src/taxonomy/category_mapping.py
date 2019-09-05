import pandas as pd
import copy
from src.exceptions.exceptions import TopParentNotCategory, NoCategoryMatched

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

def is_categ(categ, categories):
    for key in categories.keys():
        if categ in categories[key]:
            return True
    return False

def top_parent_categ(a_type, categs):
    '''
    Return the top frequent parent if it is a category
    :param a_type:
    :param categs:
    :return:
    '''
    try:
        # top_parent = parent(a_type)["parent"].iloc[0]
        top_parent = get_top_parent(a_type)
    except IndexError:
        top_parent = ""

    if is_categ(top_parent, categs):
        return top_parent
    else:
        raise TopParentNotCategory()

def get_top_parent(a_type):
    '''
    Return the top parent excluding "point_of_interest" and "establishment"
    :param a_type:
    :return:
    '''
    type_parent_df = parent(a_type)

    i = 0
    top_parent = type_parent_df["parent"].iloc[i]

    while top_parent in ["point_of_interest", "establishment"]:
        i += 1
        top_parent = type_parent_df["parent"].iloc[i]

    return top_parent


def most_general_categ(a_type, categs):
    pass

def map_type_categ(a_type, categs):
    '''
    Finds a parent category for a given type
    :param a_type:
    :param categs:
    :return:
    '''
    if is_categ(a_type, categs):
        #         print("Direct matching: >>> {}".format(a_type))
        return a_type

    else:
        #         print("Indirect matching: >>> {}".format(a_type))
        return top_parent_categ(a_type, categs)


def map_types_to_categ(types, categs):
    mapped_categs = []

    for a_type in types:
        try:
            mapped_categ = map_type_categ(a_type, categs)
            mapped_categs.append(mapped_categ)
        except TopParentNotCategory:
            continue

    return mapped_categs


def mapped_categ(types, categs):
    mapped_categs = pd.Series(map_types_to_categ(types, categs)).value_counts()
    most_frequent = mapped_categs[mapped_categs == mapped_categs.max()].index.tolist()

    if len(most_frequent) == 0:
        raise NoCategoryMatched()

    if len(most_frequent) > 1:
        return map_types_to_categ(types, categs)[0]  # most specific

    else:
        return most_frequent[0]