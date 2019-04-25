import numpy as np
from pyproj import Proj, transform
from src.utils.math import normalize

def haversine_vectorized(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in meters between two points
    on the earth (specified in decimal degrees)
    Adapted from code found at: https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
    """
    # Convert decimal degrees to Radians:
    lon1 = np.radians(lon1)
    lat1 = np.radians(lat1)
    lon2 = np.radians(lon2)
    lat2 = np.radians(lat2)
    # Implementing Haversine Formula:
    dlon = np.subtract(lon2, lon1)
    dlat = np.subtract(lat2, lat1)
    a = np.add(np.power(np.sin(np.divide(dlat, 2)), 2),
               np.multiply(np.cos(lat1),
                           np.multiply(np.cos(lat2),
                                       np.power(np.sin(np.divide(dlon, 2)), 2))))
    c = np.multiply(2, np.arcsin(np.sqrt(a)))
    r = 6371
    return c * r * 1000


def cluster_centroid(cluster):
    count = cluster["latitude"].count() # count() instead of len() to avoid count nan values
    sum_lat = cluster["latitude"].sum()
    sum_lon = cluster["longitude"].sum()
    points_centroid = {"latitude": sum_lat / count, "longitude": sum_lon / count}
    return points_centroid

def weighted_cluster_centroid(cluster, weight_col):
    w_sum_lat = (cluster["latitude"] * cluster[weight_col]).sum()
    w_sum_lon = (cluster["longitude"] * cluster[weight_col]).sum()
    points_w_centroid = {"latitude": w_sum_lat / cluster[weight_col].sum(), "longitude": w_sum_lon / cluster[weight_col].sum()}
    return points_w_centroid

def index_clusters(clusters):
    indexed_clusters = {}
    for cluster in clusters:
        cluster = cluster.sort_values(by="local_time")
        indexed_clusters[int(cluster.tail(1)["local_time"])] = cluster

    return indexed_clusters

def user_df_loc_tuples(user_df):
    return [tuple(loc) for loc in user_df[["latitude", "longitude"]].values]

def user_data_gps_to_web_mercator(user_df):
    gps_list = user_df_loc_tuples(user_df)
    return [gps_loc_to_web_mercator(lat=gps_loc[0], lon=gps_loc[1]) for gps_loc in gps_list]

def gps_loc_to_web_mercator(lat, lon):
    return transform(Proj(init='epsg:4326'), Proj(init='epsg:3857'), lon, lat)

