import pandas as pd
from src.utils import geo
from src.dao import csv_dao
from src.poi_grabber import google_places

class StopRegion:
    '''
          Use EPSG 4326
    '''
    def __init__(self, centroid_lat, centroid_lon, start_time, end_time, sr_id, semantics=[]):
        self.centroid_lat = round(centroid_lat, 5)
        self.centroid_lon = round(centroid_lon, 5)
        self.start_time = start_time
        self.end_time = end_time
        self.sr_id = sr_id

        self.user_id = sr_id.split("_")[0]
        self.close_pois = pd.DataFrame()
        self.close_pois_ids = []

        self.semantics = semantics

    def distance_to_point(self, point, lat_col="latitude", lon_col="longitude"):
        return geo.distance_epsg_4326(self.centroid_lat, self.centroid_lon,
                                      point[lat_col], point[lon_col])

    def distance_to_another_sr(self, another_sr):
        return geo.distance_epsg_4326(self.centroid_lat, self.centroid_lon,
                                      another_sr.centroid_lat, another_sr.centroid_lon)

    def delta_time_to_another_sr(self, another_sr):
        return min(abs(self.start_time - another_sr.end_time), abs(self.end_time - another_sr.start_time))

    def load_close_pois(self, verbose=False):
        if verbose:
            print("Loading POIs")

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
        return self.close_pois[self.close_pois["distance"] == self.close_pois["distance"].min()]

    def tag_radius_pois(self, radius, remove_tags=["establishment", "point_of_interest"]):
        pois_tags = self.radius_pois(radius)["types"]
        return self.__remove_tags_from_list(pois_tags.tolist(), remove_tags)

    def radius_pois(self, radius):
        return self.close_pois[self.close_pois["distance"] <= radius]

    def centroid_mercator(self):
        geo.gps_loc_to_web_mercator(self.centroid_lat, self.centroid_lon)


def sr_row_to_stop_region(sr_row):
    return StopRegion(centroid_lat = sr_row["latitude"], centroid_lon=sr_row["longitude"],
                      start_time=sr_row["local_start_time"], end_time=sr_row["local_end_time"],
                      sr_id=sr_row["sr_id"], semantics=sr_row["tag"].split(","))

if __name__ == "__main__":
    sr = StopRegion(46.7, 6.8, "1234_56")
    print(sr.centroid_mercator())

