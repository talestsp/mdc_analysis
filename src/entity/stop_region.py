import pandas as pd
from src.utils import geo
from src.dao import csv_dao
from src.poi_grabber import google_places
from src.plot import plot2

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
        self.close_pois = pd.DataFrame()
        self.close_pois_ids = []
        self.semantics = semantics
        self.agglutination = agglutination

        self.close_pois = None

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

        return close_pois_agg.set_index("place_id").merge(distances, left_index=True, right_index=True)

    def load_close_pois(self, verbose=False):
        if verbose:
            print("Loading POIs")

        if self.is_agglutination():
            self.close_pois = self.__merge_agg_pois()
            return self.close_pois

        pois = csv_dao.load_knn_pois_by_stop_region(self)[["distance", "place_id", "position"]]
        self.close_pois = google_places.load_all_google_places_data(valid_pois=True).merge(pois, on="place_id", how="inner").sort_values(by="distance")

        if verbose:
            print("{} POIs loaded".format(len(self.close_pois)))
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
        pois_tags = self.closest_poi()["types"]
        return self.__remove_tags_from_list(pois_tags.tolist(), remove_tags)

    def closest_poi(self):
        if self.close_pois is None:
            self.load_close_pois()
        return self.close_pois[self.close_pois["distance"] == self.close_pois["distance"].min()]

    def tag_radius_pois(self, radius, remove_tags=["establishment", "point_of_interest"]):
        pois_tags = self.radius_pois(radius)["types"]
        return self.__remove_tags_from_list(pois_tags.tolist(), remove_tags)

    def radius_pois(self, radius):
        if self.close_pois is None:
            self.load_close_pois()
        return self.close_pois[self.close_pois["distance"] <= radius]

    def centroid_mercator(self):
        geo.gps_loc_to_web_mercator(self.centroid_lat, self.centroid_lon)

    def plot(self, p=None):
        return plot2.plot_stop_region(self, p=p)

class StopRegionGroup:
    '''
          Use EPSG 4326
    '''
    def __init__(self, stop_region_list):
        self.stop_region_list = stop_region_list
        self.stop_region_list.sort(key=lambda x: x.start_time, reverse=False)

    def plot(self, title="", width=800, height=600, fill_color="magenta", p=None, mark_type="circle"):
        return plot2.plot_stop_region_sequence(stop_region_sequence=self, title=title, mark_type=mark_type,
                                               width=width, height=height, fill_color=fill_color, p=p)
    def size(self):
        return len(self.stop_region_list)

    def sequence_report(self):
        sequence_report = []

        last_sr = self.stop_region_list[0]

        for sr in self.stop_region_list[1:]:
            sequence_row = {"distance": round(sr.distance_to_another_sr(last_sr), 1),
                            "delta_t": sr.delta_time_to_another_sr(last_sr),
                            "last_sr": last_sr.sr_id, "last_sr_tag": last_sr.tag_closest_poi(),
                            "sr": sr.sr_id, "sr_tag": sr.tag_closest_poi(),
                            "last_sr_semantics": last_sr.semantics,
                            "sr_semantics": sr.semantics}
            sequence_report.append(sequence_row)
            last_sr = sr

        cols = ["delta_t", "distance", "last_sr_tag", "sr_tag", "last_sr_semantics", "sr_semantics", "last_sr", "sr"]
        return pd.DataFrame(sequence_report)[cols]

    def agglutinate_stop_regions(self):
        agglutinated = []
        singles = []

        agglutinated_srs, agglutination_report = group_stop_regions_for_agglutination(self.stop_region_list, same_closest_poi)

        for group in agglutinated_srs:
            if len(group) == 1:
                singles.append(group[0])
            else:
                agglutinated_stop_regions = agglutinate(group)
                agglutinated.append(StopRegion(**agglutinated_stop_regions))

        srs = agglutinated + singles
        srs.sort(key=lambda x: x.start_time, reverse=False)

        print("srs", len(srs))
        print("agglutinated", len(agglutinated))
        print("singles", len(singles))
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

    return StopRegion(centroid_lat = sr_row["latitude"], centroid_lon=sr_row["longitude"],
                      start_time=sr_row["local_start_time"], end_time=sr_row["local_end_time"],
                      user_id=sr_row["user_id"], sr_id=sr_row["sr_id"], semantics=semantics)

def same_closest_poi(last_sr, sr):
    set_sr_pois = set(sr.closest_poi()["place_id"].tolist())
    set_last_sr_pois = set(last_sr.closest_poi()["place_id"].tolist())
    return len(set_sr_pois.intersection(set_last_sr_pois)) > 0

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

def group_stop_regions_for_agglutination(sr_list, agglutination_rule):
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

        if agglutination_rule(last_sr, sr):
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

