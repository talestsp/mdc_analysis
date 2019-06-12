import pandas as pd
from src.utils import geo
from src.dao import csv_dao

class StopRegion:
    '''
          Use EPSG 4326
    '''
    def __init__(self, centroid_lat, centroid_lon, sr_id):
        self.centroid_lat = round(centroid_lat, 5)
        self.centroid_lon = round(centroid_lon, 5)
        self.sr_id = sr_id

        self.user_id = sr_id.split("_")[0]
        self.close_pois = pd.DataFrame()
        self.close_pois_ids = []

        self.tags = []


    def distance_to_point(self, point, lat_col="latitude", lon_col="longitude"):
        return geo.distance_epsg_4326(self.centroid_lat, self.centroid_lon,
                                      point[lat_col], point[lon_col])

    # def add_close_pois(self, pois):
    #     self.close_pois = self.close_pois.append(pois)
    #
    # def get_close_pois(self):
    #     return self.close_pois
    #
    # def add_close_pois_ids(self, pois_ids, load_pois=False):
    #     if type(pois_ids) is list:
    #         self.close_pois_ids = self.close_pois_ids  + pois_ids
    #     else:
    #         self.close_pois_ids.append(pois_ids)

    def load_close_pois(self):
        self.close_pois = csv_dao.load_kkn_pois_by_stop_region(self)
        return self.close_pois

    def tag_closest_poi(self):
        return self.closest_poi()["types"]

    def closest_poi(self):
        return self.close_pois[self.close_pois["distance"] == self.close_pois["distance"].min()]

    def tag_radius_poi(self, radius):
        return self.radius_pois(radius)["types"]

    def radius_pois(self, radius_m):
        return self.close_pois[self.close_pois["distance"] <= radius_m]

