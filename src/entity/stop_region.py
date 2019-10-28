import pandas as pd
from src.utils import geo
from src.dao import csv_dao
from src.poi_grabber import google_places
from src.plot import plot2
from src.utils.others import concat_lists
from src.exceptions import exceptions

class StopRegion:
    '''
          Use EPSG 4326
    '''
    def __init__(self, centroid_lat, centroid_lon, start_time, end_time, user_id, sr_id, semantics=[], agglutination=[]):
        self.centroid_lat = round(centroid_lat, 5)
        self.centroid_lon = round(centroid_lon, 5)
        self.start_time = start_time
        self.end_time = end_time
        self.sr_id = sr_id

        self.user_id = user_id
        # self.close_pois = pd.DataFrame()
        self.close_pois_ids = []
        self.semantics = semantics
        self.agglutination = agglutination

        self.close_pois = None

        self.load_close_pois()

    def agglutinate_with(self, another_stop_regions):
        agglutination_params = agglutinate([self] + another_stop_regions)
        return StopRegion(**agglutination_params)

    def is_agglutination(self):
        return len(self.agglutination) > 0

    def distance_to_point(self, point, lat_col="latitude", lon_col="longitude"):
        return geo.distance_epsg_4326(self.centroid_lat, self.centroid_lon,
                                      point[lat_col], point[lon_col])

    def distance_to_another_sr(self, another_sr):
        return geo.distance_epsg_4326(self.centroid_lat, self.centroid_lon,
                                      another_sr.centroid_lat, another_sr.centroid_lon)

    def delta_time_to_another_sr(self, another_sr):
        return min(abs(self.start_time - another_sr.end_time), abs(self.end_time - another_sr.start_time))

    def __merge_agg_pois(self):
        close_pois_agg = pd.DataFrame()

        for sr in self.agglutination:
            close_pois_agg = close_pois_agg.append(sr.close_pois)

        distances = close_pois_agg.groupby("place_id")["distance"].mean().to_frame()
        del close_pois_agg["distance"]
        close_pois_agg = close_pois_agg.drop_duplicates(subset="place_id")

        return close_pois_agg.set_index("place_id", drop=False).merge(distances, left_index=True, right_index=True)

    def load_close_pois(self, verbose=False):
        if verbose:
            print("Loading POIs")

        if self.is_agglutination():
            self.close_pois = self.__merge_agg_pois()
            return self.close_pois

        pois = csv_dao.load_knn_pois_by_stop_region(self)[["distance", "place_id", "position", "sr_id"]]
        self.close_pois = google_places.load_all_google_places_data(valid_pois=True).merge(pois, on="place_id", how="inner").sort_values(by="distance")

        if verbose:
            print("{} POIs loaded".format(len(self.close_pois)))

        if self.close_pois is None:
            print("0 pois, sr_id", self.sr_id)

        return self.close_pois

    def __remove_tags_from_list(self, tags_list, tags_to_be_removed):
        use_pois_tags = []
        for poi_types in tags_list:
            for to_be_removed in tags_to_be_removed:
                if to_be_removed in poi_types:
                    del poi_types[poi_types.index(to_be_removed)]
            use_pois_tags.append(poi_types)

        return use_pois_tags

    def tag_closest_poi(self, remove_tags=["establishment", "point_of_interest"]):
        pois_tags = self.closest_poi()["types"].apply(lambda types_list : pd.Series(types_list).drop_duplicates().tolist())
        return self.__remove_tags_from_list(pois_tags.tolist(), remove_tags)

    def closest_poi(self):
        if self.close_pois is None:
            self.load_close_pois()
        return self.close_pois[self.close_pois["distance"] == self.close_pois["distance"].min()]

    def tag_radius_pois(self, radius, remove_tags=["establishment", "point_of_interest"]):
        pois_tags = self.radius_pois(radius)["types"].apply(lambda types_list : pd.Series(types_list).drop_duplicates().tolist())
        return self.__remove_tags_from_list(pois_tags.tolist(), remove_tags)

    def radius_pois(self, radius):
        if self.close_pois is None:
            self.load_close_pois()
        return self.close_pois[self.close_pois["distance"] <= radius]

    def centroid_mercator(self):
        geo.gps_loc_to_web_mercator(self.centroid_lat, self.centroid_lon)

    def plot(self, p=None):
        return plot2.plot_stop_region_mousover(self, p=p)

    def plot_simple(self, p=None, title="", color="magenta", width=800, height=600, legend=None, mark_type="circle"):
        return plot2.plot_stop_region(self, p=p, title=title, color=color, width=width, height=height, legend=legend, mark_type=mark_type)

class StopRegionGroup:
    '''
          Use EPSG 4326
    '''
    def __init__(self, stop_region_list, agglutinate_stop_regions=False):
        self.stop_region_list = stop_region_list
        self.stop_region_list.sort(key=lambda x: x.start_time, reverse=False)

        if agglutinate_stop_regions:
            self.stop_region_list = self.agglutinate_stop_regions().stop_region_list

    def plot(self, title="", width=800, height=600, plot_n_pois=4, fill_color="magenta", p=None, mark_type="circle"):

        p = plot2.plot_stop_region_group(stop_region_group=self, title=title, mark_type=mark_type,
                                            width=width, height=height, fill_color=fill_color, p=p,
                                            plot_n_pois=plot_n_pois)

        p = plot2.mark_home_and_work(p, self)

        return p

    def search_stop_region_by_id(self, sr_id):
        for sr in self.stop_region_list:
            if sr.sr_id == sr_id:
                return sr
        return None

    def size(self):
        return len(self.stop_region_list)

    def delta_time(self):
        return self.stop_region_list[-1].end_time - self.stop_region_list[0].start_time

    def sequence_report(self, only_simple_cols=True):
        self.stop_region_list.sort(key=lambda x: x.start_time, reverse=False)

        if self.size() <= 1:
            raise exceptions.TransitionsNeedAtLeastTwoStates()

        sequence_report = []

        last_sr = self.stop_region_list[0]

        for sr in self.stop_region_list[1:]:
            sequence_row = {"distance": round(sr.distance_to_another_sr(last_sr), 1),
                            "delta_t": sr.delta_time_to_another_sr(last_sr),
                            "last_sr": last_sr.sr_id, "last_sr_type": last_sr.tag_closest_poi(),
                            "sr": sr.sr_id, "sr_type": sr.tag_closest_poi(),
                            "last_sr_semantics": last_sr.semantics,
                            "sr_semantics": sr.semantics,
                            "sr_start_time": sr.start_time,
                            "sr_end_time": sr.end_time}
            sequence_report.append(sequence_row)
            last_sr = sr

        report = pd.DataFrame(sequence_report)

        if only_simple_cols:
            simpĺe_cols = ["delta_t", "distance", "last_sr_type", "sr_type", "last_sr_semantics", "sr_semantics", "last_sr", "sr"]
            report = report[simpĺe_cols]

        return report

    def sequence_pois_type(self):
        return self.sequence_report["last_sr_tag"].tolist()

    def sequence_stop_region_types(self):
        types_list = []
        for sr in self.stop_region_list:
            sr_types_list = sr.tag_closest_poi()

            for sr_types in sr_types_list:
                types_list.append(sr_types)

        return types_list

    def sequence_stop_region_tags(self):
        '''
        The tags of the Stop Regions sequence sorted by time.
        By tags undertstand Stop Regions semantics and POIs' type.

        If a place has a semantic tag it will replace the POI type in this sequence.
        :return:
        '''

        tags = []

        for sr in self.stop_region_list:
            sequence_row = {"sr": sr.sr_id, "sr_types": sr.tag_closest_poi(),
                            "sr_semantics": sr.semantics,
                            "sr_start_time": sr.start_time,
                            "sr_end_time": sr.end_time}
            tags.append(sequence_row)

        tags_df = pd.DataFrame(tags)

        try:
            tags = tags_df.apply(
                lambda tag_dict: concat_lists(tag_dict["sr_types"]) if len(tag_dict["sr_semantics"]) == 0 else tag_dict[
                    "sr_semantics"], axis=1)
        except ValueError:
            tags = []
            for index, row in tags_df.iterrows():
                if len(row["sr_semantics"]) == 0:
                    tags.append(concat_lists(row["sr_types"]))
                else:
                    tags.append(row["sr_semantics"])

        tags_df["tag"] = tags

        return tags_df[["sr_start_time", "sr_end_time", "tag"]]

    def agglutinate_stop_regions(self):
        agglutinated = []
        singles = []

        agglutinated_srs, agglutination_report = group_stop_regions_for_agglutination(self.stop_region_list, same_closest_poi, same_not_null_semantics)

        for group in agglutinated_srs:
            if len(group) == 1:
                singles.append(group[0])
            else:
                agglutinated_stop_regions = agglutinate(group)
                agglutinated.append(StopRegion(**agglutinated_stop_regions))

        srs = agglutinated + singles
        srs.sort(key=lambda x: x.start_time, reverse=False)

        return StopRegionGroup(srs)


####################################################
####################################################

def sr_row_to_stop_region(sr_row):
    if sr_row["tag"] is None:
        semantics = []
    elif len(sr_row["tag"].split(",")) == 1 and sr_row["tag"].split(",")[0] == "":
        semantics = []
    else:
        semantics = sr_row["tag"].split(",")

    return StopRegion(centroid_lat=sr_row["latitude"], centroid_lon=sr_row["longitude"],
                      start_time=sr_row["local_start_time"], end_time=sr_row["local_end_time"],
                      user_id=sr_row["user_id"], sr_id=sr_row["sr_id"], semantics=semantics)

def same_closest_poi(last_sr, sr):
    set_sr_pois = set(sr.closest_poi()["place_id"].tolist())
    set_last_sr_pois = set(last_sr.closest_poi()["place_id"].tolist())
    return len(set_sr_pois.intersection(set_last_sr_pois)) > 0

def same_not_null_semantics(last_sr, sr):
    if not type(last_sr.semantics) is list:
        raise Exception("Malformed semantics")
    elif len(last_sr.semantics) == 0 or len(sr.semantics) == 0:
        return False

    set_sr_semantics = set(sr.semantics)
    set_last_sr_semantics = set(last_sr.semantics)
    return set_sr_semantics.intersection(set_last_sr_semantics) == set_sr_semantics .union(set_last_sr_semantics)

def close_sr_short_time(last_sr, sr, time_tolerance_secs=600, distance_tolerance_m=5):
    return sr.distance_to_another_sr(last_sr) <= distance_tolerance_m and sr.delta_time_to_another_sr(
        last_sr) <= time_tolerance_secs

def agglutinate(stop_regions):
        end_times = []
        start_times = []
        user_ids = []
        semantics = []
        gps_points = pd.DataFrame()

        early_time_sr = stop_regions[0]

        for sr in stop_regions:
            end_times.append(sr.end_time)
            start_times.append(sr.start_time)
            user_ids.append(sr.user_id)
            semantics = semantics + sr.semantics
            gps_points = gps_points.append(csv_dao.load_stop_region_by_sr_id(sr.user_id, sr.sr_id))[["latitude", "longitude"]]

            if sr.start_time < early_time_sr.start_time:
                early_time_sr = sr

        centroid = geo.cluster_centroid(gps_points)

        return {'centroid_lat': centroid["latitude"],
                'centroid_lon': centroid["longitude"],
                'start_time': pd.Series(start_times).min(),
                'end_time': pd.Series(end_times).max(),
                'sr_id': "agg_{}".format(early_time_sr.sr_id),
                'user_id': early_time_sr.user_id,
                'semantics': pd.Series(semantics).drop_duplicates().tolist(),
                'agglutination': stop_regions}

def group_stop_regions_for_agglutination(sr_list, agglutination_rule_1, agglutination_rule_2):
    agglutinate = [[sr_list[0]]]
    agglutination_report = []

    last_sr = sr_list[0]
    for sr in sr_list[1:]:
        agglutination_report_row = {"distance": round(sr.distance_to_another_sr(last_sr), 1),
                                    "delta_t": sr.delta_time_to_another_sr(last_sr),
                                    "last_sr": last_sr.sr_id, "last_sr_tag": last_sr.tag_closest_poi(),
                                    "sr": sr.sr_id, "sr_tag": sr.tag_closest_poi(),
                                    "last_sr_semantics": last_sr.semantics,
                                    "sr_semantics": sr.semantics}

        if agglutination_rule_1(last_sr, sr) or agglutination_rule_2(last_sr, sr):
            agglutinate[-1].append(sr)
            agglutination_report_row["agglutinate"] = True

        else:
            agglutinate.append([sr])
            agglutination_report_row["agglutinate"] = False

        agglutination_report.append(agglutination_report_row)
        last_sr = sr

    return agglutinate, pd.DataFrame(agglutination_report)[
        ["agglutinate", "delta_t", "distance", "last_sr_tag", "sr_tag", "last_sr_semantics", "sr_semantics", "last_sr", "sr"]]


# def agglutinate_stop_regions(self):
#     agglutinated = []
#     singles = []
#
#     grouped_stop_regions, agglutination_report = group_stop_regions_for_agglutination(self.stop_region_sequence, same_closest_poi)
#
#     for group in grouped_stop_regions:
#         if len(group) == 1:
#             singles.append(group[0])
#         else:
#             agg_sr = agglutinate(group)
#             agglutinated.append(StopRegion(**agg_sr))
#
#     return StopRegionSequence((agglutinated + singles).sort(key=lambda x: x.start_time, reverse=False))


if __name__ == "__main__":
    sr = StopRegion(46.7, 6.8, "1234_56")
    print(sr.centroid_mercator())

