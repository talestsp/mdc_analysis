import pandas as pd
from src.utils import geo

class StropRegion:
    '''
          Use EPSG 4326
    '''
    def __init__(self, centroid_lat, centroid_lon, id=None):
        self.centroid_lat = centroid_lat
        self.centroid_lon = centroid_lon
        self.id = id

        self.close_pois = pd.DataFrame()

    def distance_to_point(self, point, lat_col="latitude", lon_col="longitude"):
        return geo.distance_epsg_4326(self.centroid_lat, self.centroid_lon,
                                      point[lat_col], point[lon_col])

    def add_close_pois(self, pois):
        self.close_pois = self.close_pois.append(pois)

    def get_close_pois(self):
        return self.close_pois
