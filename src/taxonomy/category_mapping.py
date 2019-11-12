from itertools import groupby

from src.taxonomy.category_mapper import CategoryMapper
from src.utils.others import remove_list_elements
from src.exceptions.exceptions import NoCategoryMatched, NotValidTypes


CATEG_MAPPER = None

def tags_to_categ(user_tags_dict, version="0.1.categ_v1"):
    if not CATEG_MAPPER:
        categ_mapper = CategoryMapper()
        CATEG_MAPPER = categ_mapper
    else:
        categ_mapper = CATEG_MAPPER

    users_categ_sequence = {}
    users_categ_sequence_elements = {}

    n = 0
    for user_id in list(user_tags_dict.keys()):
        n += 1
        print("n:", n, "user_id:", user_id)

        user_tags_dict[user_id] = clean_sequence(user_tags_dict[user_id])

        if len(remove_list_elements(user_tags_dict[user_id], elements=[[]])) < 8:
            continue

        categ_sequence = []

        for tags in user_tags_dict[user_id]:
            if tags == ["WORK"] or tags == ["HOME"]:
                categ_sequence.append(tags)

            else:
                try:
                    categ = categ_mapper.map_categ(tags, method="most_specific")
                    categ_sequence.append([categ])

                except NotValidTypes:
                    pass

                except NoCategoryMatched:
                    categ_sequence.append(["NoCategoryMatched"])

        if version == "0.1.categ_v1":
            users_categ_sequence[user_id] = agglutinate_consecutive_elements(categ_sequence)
            users_categ_sequence_elements[user_id] = [categ[0] for categ in users_categ_sequence[user_id]]

        else:
            users_categ_sequence[user_id] = categ_sequence
            users_categ_sequence_elements[user_id] = [categ[0] for categ in categ_sequence]

    return users_categ_sequence, users_categ_sequence_elements

# class CategoryMapping:
#
#     def __init__(self):
#         self.categ_mapper = None
#
#     def tags_to_categ(self, user_tags_dict, version="0.1.categ_v1"):
#         if not self.categ_mapper:
#             self.categ_mapper = CategoryMapper()
#
#         users_categ_sequence = {}
#         users_categ_sequence_elements = {}
#
#         n = 0
#         for user_id in list(user_tags_dict.keys()):
#             n += 1
#             print("n:", n, "user_id:", user_id)
#
#             user_tags_dict[user_id] = clean_sequence(user_tags_dict[user_id])
#
#             if len(remove_list_elements(user_tags_dict[user_id], elements=[[]])) < 8:
#                 continue
#
#             categ_sequence = []
#
#             for tags in user_tags_dict[user_id]:
#                 if tags == ["WORK"] or tags == ["HOME"]:
#                     categ_sequence.append(tags)
#
#                 else:
#                     try:
#                         categ = self.categ_mapper.map_categ(tags, method="most_specific")
#                         categ_sequence.append([categ])
#
#                     except NotValidTypes:
#                         pass
#
#                     except NoCategoryMatched:
#                         categ_sequence.append(["NoCategoryMatched"])
#
#             if version == "0.1.categ_v1":
#                 users_categ_sequence[user_id] = agglutinate_consecutive_elements(categ_sequence)
#                 users_categ_sequence_elements[user_id] = [categ[0] for categ in users_categ_sequence[user_id]]
#
#             else:
#                 users_categ_sequence[user_id] = categ_sequence
#                 users_categ_sequence_elements[user_id] = [categ[0] for categ in categ_sequence]
#
#         return users_categ_sequence, users_categ_sequence_elements



def clean_sequence(sequence):
    new_sequence = []

    for tags in sequence:
        if "parking" in tags:
            continue
        else:
            new_sequence.append(tags)

    return new_sequence


def agglutinate_consecutive_elements(a_list):
    return [x[0] for x in groupby(a_list)]