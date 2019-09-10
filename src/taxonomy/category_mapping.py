import pandas as pd
import json

from src.exceptions.exceptions import TopParentNotCategory, NoCategoryMatched
from src.utils.type_hierarchy_analysis import parent, relations_freq
from src.poi_grabber import google_places
from src.utils.others import remove_list_elements
from src.exceptions.exceptions import NotValidTypes

class CategoryMapper:

    def __init__(self):
        self.categories = self._load_categories()
        self.relations_freq = relations_freq(google_places.load_all_google_places_data(valid_pois=True))

    def _load_categories(self):
        with open('outputs/taxonomy/google_places/categories.csv') as json_file:
            return json.load(json_file)

    def _map_type_categ(self, a_type, categs):
        '''
        Finds a parent category for a given type. If the given type is already a category it returns the type.
        :param a_type:
        :param categs:
        :return:
        '''
        if self._is_categ(a_type, categs):
            return a_type

        else:
            return self._top_parent_categ(a_type, categs)

    def _is_categ(self, categ, categories):
        for key in categories.keys():
            if categ in categories[key]:
                return True
        return False

    def _get_top_parent(self, a_type):
        '''
        Return the top parent excluding "point_of_interest" and "establishment"
        :param a_type:
        :return:
        '''
        type_parent_df = parent(a_type, self.relations_freq)

        i = 0
        top_parent = type_parent_df["parent"].iloc[i]

        while top_parent in ["point_of_interest", "establishment"]:
            i += 1
            top_parent = type_parent_df["parent"].iloc[i]

        return top_parent

    def _top_parent_categ(self, a_type, categs):
        '''
        Return the top frequent parent if it is a category
        :param a_type:
        :param categs:
        :return:
        '''
        try:
            # top_parent = parent(a_type)["parent"].iloc[0]
            top_parent = self._get_top_parent(a_type)
        except IndexError:
            top_parent = ""

        if self._is_categ(top_parent, categs):
            return top_parent
        else:
            raise TopParentNotCategory()

    def _map_types_to_categ(self, types, categs):
        mapped_categs = []

        for a_type in types:
            try:
                mapped_categ = self._map_type_categ(a_type, categs)
                mapped_categs.append(mapped_categ)
            except TopParentNotCategory:
                continue

        return mapped_categs

    def _most_specific(self, categories):
        return categories[0]

    def _valid_types(self, types):
        clean_types = remove_list_elements(types, elements=['premise', 'point_of_interest', 'establishment'])
        if len(clean_types) == 0:
            raise NotValidTypes

        return clean_types

    def map_categ(self, types, logs=False):
        types = self._valid_types(types)
        mapped = self._map_types_to_categ(types, self.categories)

        mapped_categs = pd.Series(mapped).value_counts()
        most_frequent = mapped_categs[mapped_categs == mapped_categs.max()].index.tolist()

        if logs:
            print("\n---")
            print("TYPES :", types)
            print("\nMAPPED:", mapped)
            print("most_frequent:", most_frequent)

        if len(most_frequent) == 0:
            raise NoCategoryMatched()

        if len(most_frequent) > 1:
            return self._most_specific(mapped)

        else:
            return most_frequent[0]


if __name__ == "__main__":
    print("RUN!")

    categs = []
    not_found = []

    from src.poi_grabber import google_places

    d = google_places.load_all_google_places_data(valid_pois=True)

    print(len(d))

    for i, poi in d.iterrows():
        try:
            categ = CategoryMapper().map_categ(poi["types"], logs=False)
            # print("CATEG:", categ, "<<<")
            categs.append(categ)
            if "premise" in poi["types"]:
                print(poi["types"])

        except NoCategoryMatched:
            categs.append("NoCategoryMatched")
            not_found.append(poi["types"])

    print(not_found)

    print("\nfinished!")