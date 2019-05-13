import numpy as np
import pandas as pd
from pyproj import Proj, transform
from src.dao import csv_dao

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


def box_limits(users):
    global_min_lon = 999999999
    global_min_lat = 999999999
    global_max_lat = -999999999
    global_max_lon = -999999999

    for userid in users:
        user_gps_data = csv_dao.load_user_gps_csv(userid=userid)
        if len(user_gps_data) == 0:
            continue

        user_min_lat = user_gps_data["latitude"].min()
        user_min_lon = user_gps_data["longitude"].min()
        user_max_lat = user_gps_data["latitude"].max()
        user_max_lon = user_gps_data["longitude"].max()

        if user_min_lat < global_min_lat:
            global_min_lat = user_min_lat

        if user_max_lat > global_max_lat:
            global_max_lat = user_max_lat

        if user_min_lon < global_min_lon:
            global_min_lon = user_min_lon

        if user_max_lon > global_max_lon:
            global_max_lon = user_max_lon

    return {"min_lon": global_min_lon, "max_lon": global_max_lon,
            "min_lat": global_min_lat, "max_lat": global_max_lat}


def bounding_box(users):
    limits = box_limits(users)

    p3 = {"latitude": limits["min_lat"], "longitude": limits["min_lon"]}
    p4 = {"latitude": limits["min_lat"], "longitude": limits["max_lon"]}
    p2 = {"latitude": limits["max_lat"], "longitude": limits["min_lon"]}
    p1 = {"latitude": limits["max_lat"], "longitude": limits["max_lon"]}

    return pd.DataFrame([p1, p2, p3, p4])


def user_bounding_box(user_id, expand=None):
    box = bounding_box([user_id])

    if expand is None:
        return box

    else:
        p1, p2, p3, p4 = box.iloc[0], box.iloc[1], box.iloc[2], box.iloc[3]

        p1["longitude"] = p1["longitude"] + abs(p1["longitude"] - p2["longitude"]) * expand
        p1["latitude"] = p1["latitude"] + abs(p1["latitude"] - p4["latitude"]) * expand

        p2["longitude"] = p2["longitude"] - abs(p1["longitude"] - p2["longitude"]) * expand
        p2["latitude"] = p2["latitude"] + abs(p2["latitude"] - p3["latitude"]) * expand

        p3["longitude"] = p3["longitude"] - abs(p4["longitude"] - p3["longitude"]) * expand
        p3["latitude"] = p3["latitude"] - abs(p2["latitude"] - p3["latitude"]) * expand

        p4["longitude"] = p4["longitude"] + abs(p4["longitude"] - p3["longitude"]) * expand
        p4["latitude"] = p4["latitude"] - abs(p1["latitude"] - p4["latitude"]) * expand

        expanded_box = pd.DataFrame([p1.to_dict(), p2.to_dict(), p3.to_dict(), p4.to_dict()])

        return expanded_box
