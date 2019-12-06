from src.dao import objects_dao
from src.taxonomy.category_mapping import tags_to_categ
from src.exceptions.exceptions import StopRegionMinTimeNotLoaded, VersionNotRegistered, MinStopRegionTimeIs5Min


class InputDataManager:

    def __init__(self, other_sr_stay_time_thresholds_minutes=[]):
        for other_sr_stay_time_min_threshold in other_sr_stay_time_thresholds_minutes:
            if other_sr_stay_time_min_threshold < 5:
                raise MinStopRegionTimeIs5Min()

        print("Loading min_threshold data: {} min".format(5))
        self.tags_sequence_5_min_sr = objects_dao.load_users_tags_sequence(sr_stay_time_above_h=None)["original"]

        self.tags_sequence_sr_min_times = {}

        for sr_stay_time in other_sr_stay_time_thresholds_minutes:
            sr_stay_time_h = sr_stay_time / 60.
            print("Loading min_threshold data: {} min".format(sr_stay_time))
            self.tags_sequence_sr_min_times[sr_stay_time] = objects_dao.load_users_tags_sequence(sr_stay_time_above_h=sr_stay_time_h)["filtered"]

        self.tags_sequence_sr_min_times[5] = self.tags_sequence_5_min_sr

        self.versions = {}
        self.versions_other_sr_min_times = {}

    def get_input_data(self, version, sr_min_time=5):

        if not sr_min_time in self.tags_sequence_sr_min_times.keys():
            raise StopRegionMinTimeNotLoaded()

        try:
            input_data = self.versions[version]

        except KeyError:

            if version == "markov-0.0":
                input_data = self.__markov_0_0(sr_min_time=sr_min_time)
                self.versions["markov-0.0"] = input_data

            elif version == "0.0.categ_v1":
                input_data = self.__0_0_categ_v1(sr_min_time=sr_min_time)
                self.versions["0.0.categ_v1"] = input_data

            elif version == "0.1.categ_v1":
                input_data = self.__0_1_categ_v1(sr_min_time=sr_min_time)
                self.versions["0.1.categ_v1"] = input_data

            else:
                raise VersionNotRegistered()

        return input_data

    def get_user_ids(self):
        return self.tags_sequence_5_min_sr.keys()

    def __markov_0_0(self, sr_min_time=5):
        if sr_min_time == 5:
            return self.tags_sequence_5_min_sr
        else:
            return self.tags_sequence_sr_min_times[sr_min_time]

    def __0_0_categ_v1(self, sr_min_time=5):
        if sr_min_time == 5:
            return tags_to_categ(self.tags_sequence_5_min_sr, version="0.0.categ_v1", verbose=False)[0]
        else:
            return tags_to_categ(self.tags_sequence_sr_min_times[sr_min_time], version="0.0.categ_v1", verbose=False)[0]

    def __0_1_categ_v1(self, sr_min_time=5):
        if sr_min_time == 5:
            return tags_to_categ(self.tags_sequence_5_min_sr, version="0.1.categ_v1", verbose=False)[0]
        else:
            return tags_to_categ(self.tags_sequence_sr_min_times[sr_min_time], version="0.1.categ_v1", verbose=False)[0]

