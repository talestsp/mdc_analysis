from src.plot import plot
from src.utils import geo

class GeoCircle:
    '''
          Use EPSG 4326
    '''
    def __init__(self, center_lat, center_lon, radius_m, searching_tolerance=None, id=None, data=None):
        self.center_lat = center_lat
        self.center_lon = center_lon
        self.radius_m = radius_m
        self.searching_tolerance = searching_tolerance
        self.id = id
        self.data = data

    def __str__(self):
        return "Center Lat: {} \nCenter Lon: {} \nRadius (m) {}".format(self.center_lat, self.center_lon, self.radius_m)

    def put_data(self, data):
        self.data = data

    def get_data(self):
        return self.data

    def contains_point(self, latitude, longitude):
        d = geo.distance_epsg_4326(self.center_lat, self.center_lon, latitude, longitude)
        return d <= self.radius_m

    def contains_geo_circle(self, another_geo_circle):
        d = geo.distance_epsg_4326(self.center_lat, self.center_lon, another_geo_circle.center_lat, another_geo_circle.center_lon)
        return (d + another_geo_circle.radius_m) <= self.radius_m

    def plot(self, title="", color=None, width=600, height=400, legend=None, p=None):
        return plot.plot_request_circle(self, title=title, color=color, width=width, height=height, p=p, legend=legend)

