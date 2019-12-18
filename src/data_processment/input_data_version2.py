from src.dao import objects_dao, csv_dao
from src.data_processment.trajectory_cutting import gaps_params
from src.taxonomy.category_mapping import tags_to_categ
from src.exceptions.exceptions import VersionNotRegistered, MinStopRegionTimeIs5Min

DATA_VERSIONS = ["raw_tags-0.0", "0.0.categ_v1", "0.1.categ_v1"]

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

    def get_input_data(self, version, cutting_gap_time_thresh=None, sr_stay_time_minutes=5):

        try:
            input_data = self.cache[version][sr_stay_time_minutes]

        except KeyError:

            if version == "raw_tags-0.0":
                input_data = self.__raw_tags_0_0(sr_stay_time_minutes=sr_stay_time_minutes)

            elif version == "0.0.categ_v1":
                input_data = self.__0_0_categ_v1(sr_stay_time_minutes=sr_stay_time_minutes)

            elif version == "0.1.categ_v1":
                input_data = self.__0_1_categ_v1(sr_stay_time_minutes=sr_stay_time_minutes)

            else:
                raise VersionNotRegistered()

            if self.__use_cache():
                self.__insert_in_lvl_2_cache(place=[version, sr_stay_time_minutes], value=input_data)

        if cutting_gap_time_thresh is None:
            data_format = "SINGLE_TRAJECTORY"
        else:
            data_format = "MULTI_TRIPS"

        return {"user_data": input_data,
                "version": version,
                "sr_stay_time_minutes": sr_stay_time_minutes,
                "data_format": data_format}

    def get_user_ids(self):
        return self.users_seq_report.keys()

    def __user_gaps_params(self, user_id, gap_tresh_minutes):
        user_gaps = gaps_params(user_gps_data=csv_dao.load_user_gps_csv(user_id),
                                gap_tresh_minutes=gap_tresh_minutes)

        return user_gaps.to_dict(orient="records")

    def __filter_sr_by_minimum_stay_time_minutes(self, sr_stay_time_minutes):
        users_filtered_tags = {}
        sr_stay_time_h = sr_stay_time_minutes / 60.0

        for user_id in self.users_seq_report.keys():
            seq_report = self.users_seq_report[user_id]
            seq_report_filtered = seq_report[seq_report["stay_time_h"] >= sr_stay_time_h]
            users_filtered_tags[user_id] = seq_report_filtered["tags"]

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
            raw_tags[user_id] = [single_element_list[0] for single_element_list in  users_raw_traj[user_id].tolist()]
        return raw_tags

    def __0_0_categ_v1(self, sr_stay_time_minutes=5):
        tags_sequence = self.__filter_sr_by_minimum_stay_time_minutes(sr_stay_time_minutes=sr_stay_time_minutes)
        return tags_to_categ(tags_sequence, version="0.0.categ_v1", verbose=False)[1]

    def __0_1_categ_v1(self, sr_stay_time_minutes=5):
        tags_sequence = self.__filter_sr_by_minimum_stay_time_minutes(sr_stay_time_minutes=sr_stay_time_minutes)
        return tags_to_categ(tags_sequence, version="0.1.categ_v1", verbose=False)[1]


