from itertools import groupby

from src.dao import objects_dao, csv_dao
from src.data_processment.trajectory_cutting import gaps_params
from src.taxonomy.category_mapping import users_tags_to_categ, do_tags_to_categ
from src.exceptions.exceptions import VersionNotRegistered, MinStopRegionTimeIs5Min
from src.data_processment.trajectory_cutting import cut_traj_in_trips


DATA_VERSIONS = ["raw_tags-0.0", "raw_tags-0.1", "0.0.categ_v1", "0.1.categ_v1"]

class InputDataManager:

    def __init__(self, use_cache=True):
        print("Loading Users Sequence Report")
        self.users_seq_report = objects_dao.load_users_sequence_report(use_cache=use_cache)
        self.use_cache = use_cache
        self.cache = {}

    def avaliable_versions(self):
        return DATA_VERSIONS

    def __use_cache(self):
        return self.use_cache

    def get_input_data(self, version, sr_stay_time_minutes=5):

        try:
            input_data = self.cache[version][sr_stay_time_minutes]

        except KeyError:

            if version == "raw_tags-0.0":
                input_data = self.__raw_tags_0_0(sr_stay_time_minutes=sr_stay_time_minutes)

            elif version == "raw_tags-0.1":
                input_data = self.__raw_tags_0_1(sr_stay_time_minutes=sr_stay_time_minutes)

            elif version == "0.0.categ_v1":
                input_data = self.__0_0_categ_v1(sr_stay_time_minutes=sr_stay_time_minutes)

            elif version == "0.1.categ_v1":
                input_data = self.__0_1_categ_v1(sr_stay_time_minutes=sr_stay_time_minutes)

            else:
                raise VersionNotRegistered()

            if self.__use_cache():
                self.__insert_in_lvl_2_cache(place=[version, sr_stay_time_minutes], value=input_data)

        return {"user_data": input_data,
                "version": version,
                "sr_stay_time_minutes": sr_stay_time_minutes}

    def get_user_ids(self):
        return self.users_seq_report.keys()

    def users_multi_trip_stop_regions(self, gap_tresh_minutes, sr_stay_time_minutes=5):
        users_multi_trip_dict = {}

        users_seq_report = self.__filter_sr_by_minimum_stay_time_minutes(sr_stay_time_minutes)

        for user_id in self.users_seq_report:
            user_gps_data = csv_dao.load_user_gps_csv(user_id)

            multi_trip_stop_region = cut_traj_in_trips(srg_sequence_report=users_seq_report[user_id],
                                                       gaps=gaps_params(user_gps_data, gap_tresh_minutes=gap_tresh_minutes))

            users_multi_trip_dict[user_id] = multi_trip_stop_region

        return users_multi_trip_dict

    def users_multi_trip(self, gap_tresh_minutes, sr_stay_time_minutes=5, version="0.1.categ_v1"):
        users_multi_trip_sr = self.users_multi_trip_stop_regions(gap_tresh_minutes, sr_stay_time_minutes)

        users_multi_trip_dict = {}

        for user_id in users_multi_trip_sr.keys():

            if version == "raw_tags-0.0":
                users_multi_trip_dict[user_id] = [sr["tags"] for sr in users_multi_trip_sr[user_id]]

            elif version == "raw_tags-0.1":
                tags_multi_trip = self.__estract_tags_from_multi_trip(users_multi_trip_sr[user_id])
                users_multi_trip_dict[user_id] = self.__agglutinate_consecutive_elements(tags_multi_trip)

            elif version == "0.0.categ_v1":
                tags_multi_trip = self.__estract_tags_from_multi_trip(users_multi_trip_sr[user_id])
                if user_id == "6015":
                    verbose = True
                else:
                    verbose = False
                users_multi_trip_dict[user_id] = self.__tags_multi_trip_to_categs_multi_trip(tags_multi_trip, verbose=verbose)

            elif version == "0.1.categ_v1":
                tags_multi_trip = self.__estract_tags_from_multi_trip(users_multi_trip_sr[user_id])
                categs_multi_trip = self.__tags_multi_trip_to_categs_multi_trip(tags_multi_trip)
                users_multi_trip_dict[user_id] = self.__agglutinate_multi_trip_consecutive_elements(categs_multi_trip)

        return users_multi_trip_dict

    def __agglutinate_multi_trip_consecutive_elements(self, elements_multi_trip):
        agglutinated = []

        for elements in elements_multi_trip:
            agglutinated.append(self.__agglutinate_consecutive_elements(elements))

        return agglutinated

    def __tags_multi_trip_to_categs_multi_trip(self, tags_multi_trip, verbose=False):
        categs_multi_trip = []

        for tags in tags_multi_trip:
            categs = do_tags_to_categ(tags, verbose=verbose)
            categs_multi_trip.append(categs)

        return categs_multi_trip

    def __estract_tags_from_multi_trip(self, multi_trip):
        only_tags = []

        for trip in multi_trip:
            only_tags.append([sr["tags"] for sr in trip])

        return only_tags

    def __agglutinate_consecutive_elements(self, a_list):
        return [x[0] for x in groupby(a_list)]

    def __filter_sr_by_minimum_stay_time_minutes(self, sr_stay_time_minutes):
        users_filtered_tags = {}
        sr_stay_time_h = sr_stay_time_minutes / 60.0

        for user_id in self.users_seq_report.keys():
            seq_report = self.users_seq_report[user_id]
            seq_report_filtered = seq_report[seq_report["stay_time_h"] >= sr_stay_time_h]
            users_filtered_tags[user_id] = seq_report_filtered

        return users_filtered_tags

    def __insert_in_lvl_2_cache(self, place, value):
        if not place[0] in self.cache.keys():
            self.cache[place[0]] = {place[1]: value}

        elif not place[1] in self.cache[place[0]].keys():
            self.cache[place[0]][place[1]] = value

    def __raw_tags_0_0(self, sr_stay_time_minutes=5):
        raw_tags = {}
        users_raw_traj = self.__filter_sr_by_minimum_stay_time_minutes(sr_stay_time_minutes=sr_stay_time_minutes)
        for user_id in users_raw_traj.keys():
            raw_tags[user_id] = [single_element_list for single_element_list in users_raw_traj[user_id]["tags"].tolist()]
        return raw_tags

    def __raw_tags_0_1(self, sr_stay_time_minutes=5):
        raw_tags = {}
        users_raw_traj = self.__filter_sr_by_minimum_stay_time_minutes(sr_stay_time_minutes=sr_stay_time_minutes)
        for user_id in users_raw_traj.keys():
            tags = [single_element_list for single_element_list in users_raw_traj[user_id]["tags"].tolist()]
            raw_tags[user_id] = self.__agglutinate_consecutive_elements(tags)
        return raw_tags

    def __0_0_categ_v1(self, sr_stay_time_minutes=5):
        stop_regions = self.__filter_sr_by_minimum_stay_time_minutes(sr_stay_time_minutes=sr_stay_time_minutes)
        tags_sequence = {}

        for user_id in stop_regions.keys():
            tags_sequence[user_id] = stop_regions[user_id]["tags"]
        return users_tags_to_categ(tags_sequence, version="0.0.categ_v1", verbose=False)[1]

    def __0_1_categ_v1(self, sr_stay_time_minutes=5):
        stop_regions = self.__filter_sr_by_minimum_stay_time_minutes(sr_stay_time_minutes=sr_stay_time_minutes)
        tags_sequence = {}

        for user_id in stop_regions.keys():
            tags_sequence[user_id] = stop_regions[user_id]["tags"]
        return users_tags_to_categ(tags_sequence, version="0.1.categ_v1", verbose=False)[1]


