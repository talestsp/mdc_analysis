from itertools import groupby

from src.taxonomy.category_mapper import CategoryMapper
from src.utils.others import remove_list_elements
from src.exceptions.exceptions import NoCategoryMatched, NotValidTypes, VersionNotRegistered


cache = {}

def users_tags_to_categ(user_tags_dict, version="0.1.categ_v1", verbose=True):
    # if not "CATEG_MAPPER" in cache.keys():
    #     categ_mapper = CategoryMapper()
    #     cache["CATEG_MAPPER"] = categ_mapper
    # else:
    #     categ_mapper = cache["CATEG_MAPPER"]

    users_categ_sequence = {}
    users_categ_sequence_elements = {}

    n = 0
    for user_id in list(user_tags_dict.keys()):
        n += 1
        if verbose:
            print("n:", n, "user_id:", user_id)

        user_tags_dict[user_id] = clean_sequence(user_tags_dict[user_id])

        # if len(remove_list_elements(user_tags_dict[user_id], elements=[[]])) < 8:
        #     continue

        categ_sequence = do_tags_to_categ(user_tags_dict[user_id])

        if version == "0.1.categ_v1":
            users_categ_sequence[user_id] = agglutinate_consecutive_elements(categ_sequence)
            users_categ_sequence_elements[user_id] = [categ[0] for categ in users_categ_sequence[user_id]]

        elif version == "0.0.categ_v1":
            users_categ_sequence[user_id] = categ_sequence
            users_categ_sequence_elements[user_id] = [categ[0] for categ in categ_sequence]

        else:
            raise VersionNotRegistered()

    return users_categ_sequence, users_categ_sequence_elements

def do_tags_to_categ(tags_list, verbose=False):
    if not "CATEG_MAPPER" in cache.keys():
        categ_mapper = CategoryMapper()
        cache["CATEG_MAPPER"] = categ_mapper
    else:
        categ_mapper = cache["CATEG_MAPPER"]

    categ_sequence = []

    for tags in tags_list:
        if tags == ["WORK"] or tags == ["HOME"]:
            categ_sequence.append(tags)

        else:
            try:
                categ = categ_mapper.map_categ(tags, method="most_specific")
                if verbose:
                    print("TYPES:", tags)
                    print("CATEG:", categ)
                    print()
                categ_sequence.append([categ])

            except NotValidTypes:
                categ_sequence.append(["NotValidTypes"])

            except NoCategoryMatched:
                categ_sequence.append(["NoCategoryMatched"])

    return categ_sequence

def clean_sequence(sequence):
    new_sequence = []

    for tags in sequence:
        if "parking" in tags:
            new_sequence.append([])
        else:
            new_sequence.append(tags)

    return new_sequence

def agglutinate_consecutive_elements(a_list):
    return [x[0] for x in groupby(a_list)]
