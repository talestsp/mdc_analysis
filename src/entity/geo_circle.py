from src.utils import geo

class GeoCircle:
    '''
          Use EPSG 4326
    '''
    def __init__(self, center_lat, center_lon, radius_m, id=None, data=None):
        self.center_lat = center_lat
        self.center_lon = center_lon
        self.radius_m = radius_m
        self.id = id
        self.data = data

    def __str__(self):
        return "Center Lat: {} \nCenter Lon: {} \nRadius (m) {}".format(self.center_lat, self.center_lon, self.radius_m)

    def contains_point(self, latitude, longitude):
        return geo.distance_epsg_4326(self.center_lat, self.center_lon, latitude, longitude) <= self.radius_m


    def contains_geo_circle(self, another_geo_circle):
        d = geo.distance_epsg_4326(self.center_lat, self.center_lon, another_geo_circle.center_lat, another_geo_circle.center_lon)
        return (d + another_geo_circle.radius_m) <= self.radius_m
        

