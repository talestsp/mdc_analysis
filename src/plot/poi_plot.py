from src.dao import poi_dao
from src.utils.geo import gps_loc_to_web_mercator

def add_google_pois(figure):
    pois = poi_dao.load_google_pois()
    for poi in pois:
        figure = add_poi_to_figure(figure, poi, "green")

    return figure

def add_foursquare_pois(figure):
    pois = poi_dao.load_foursquare_pois()
    for poi in pois:
        figure = add_poi_to_figure(figure, poi, "blue")

    return figure

def add_poi_to_figure(figure, poi, color):
    lon, lat = gps_loc_to_web_mercator(lat=poi["lat"], lon=poi["lon"])
    figure.cross(lon, lat, color=color, size=10)

    return figure

