import numpy as np
import pandas as pd
import geopy.distance as gp
from pyproj import Proj, transform
#from src.dao import csv_dao

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
    '''
    The
    :param cluster:
    :param weight_col:
    :return:
    '''
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

def user_df_loc_tuples(user_df, lat_col="latitude", lon_col="longitude"):
    return [tuple(loc) for loc in user_df[[lat_col, lon_col]].values]

def user_data_gps_to_web_mercator(user_df, lat_col="latitude", lon_col="longitude"):
    gps_list = user_df_loc_tuples(user_df, lat_col=lat_col, lon_col=lon_col)
    return [gps_loc_to_web_mercator(lat=gps_loc[0], lon=gps_loc[1]) for gps_loc in gps_list]

def gps_loc_to_web_mercator(lat, lon):
    return transform(Proj(init='epsg:4326'), Proj(init='epsg:3857'), lon, lat)

def convert_3857_4326(lat, lon):
    inProj  = Proj("+init=EPSG:3857")
    outProj = Proj("+init=EPSG:4326")
    return transform(inProj,outProj,lat,lon)

def convert_4326_3857(lat, lon):
    raise Exception("Use funcion: {}".format("gps_loc_to_web_mercator"))
    # inProj  = Proj("+init=EPSG:4326")
    # outProj = Proj("+init=EPSG:3857")
    # return transform(inProj,outProj,lat,lon)


# def box_limits(users):
#     global_min_lon = 999999999
#     global_min_lat = 999999999
#     global_max_lat = -999999999
#     global_max_lon = -999999999
#
#     for userid in users:
#         user_gps_data = csv_dao.load_user_gps_csv(userid=userid)
#         if len(user_gps_data) == 0:
#             continue
#
#         user_min_lat = user_gps_data["latitude"].min()
#         user_min_lon = user_gps_data["longitude"].min()
#         user_max_lat = user_gps_data["latitude"].max()
#         user_max_lon = user_gps_data["longitude"].max()
#
#         if user_min_lat < global_min_lat:
#             global_min_lat = user_min_lat
#
#         if user_max_lat > global_max_lat:
#             global_max_lat = user_max_lat
#
#         if user_min_lon < global_min_lon:
#             global_min_lon = user_min_lon
#
#         if user_max_lon > global_max_lon:
#             global_max_lon = user_max_lon
#
#     return {"min_lon": global_min_lon, "max_lon": global_max_lon,
#             "min_lat": global_min_lat, "max_lat": global_max_lat}


def box_limits(users, csv_dao):
    #receiving csv_dao to avoid circular imports
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

def box_limits_by_data(gps_data):
    user_min_lat = gps_data["latitude"].min()
    user_min_lon = gps_data["longitude"].min()
    user_max_lat = gps_data["latitude"].max()
    user_max_lon = gps_data["longitude"].max()

    return {"min_lon": user_min_lon, "max_lon": user_max_lon,
            "min_lat": user_min_lat, "max_lat": user_max_lat}

def distance_epsg_4326(lat1, lon1, lat2, lon2):
    coords1 = (lat1, lon1)
    coords2 = (lat2, lon2)
    distance = gp.distance(coords1, coords2).m #utiliza o modelo WGS-84
    return distance

def distance_stop_region_pois(s_region, pois):
    distances = []
    for index, poi in pois.iterrows():
        d = distance_epsg_4326(s_region["latitude"], s_region["longitude"], poi["lat_4326"], poi["lon_4326"])
        distances.append({"osm_id": poi["osm_id"], "distance": d})

    return pd.DataFrame(distances)

def distance_stop_region_google_places(s_region, pois):
    distances = []
    for index, poi in pois.iterrows():
        d = distance_epsg_4326(s_region["latitude"], s_region["longitude"], poi["lat_4326"], poi["lon_4326"])
        distances.append({"place_id": poi["place_id"], "distance": d})

    return pd.DataFrame(distances)

def knn_stop_region(sr_centroid, valid_pois, k):
    distances = distance_stop_region_pois(sr_centroid, valid_pois)
    distances = distances.sort_values(by="distance")
    return distances.head(k)

def knn_stop_region_google_places(sr_centroid, valid_pois, k):
    distances = distance_stop_region_google_places(sr_centroid, valid_pois)
    distances = distances.sort_values(by="distance")
    return distances.head(k)

def knn_pois(centroids, pois, k):
    user_knn = []
    for index, centroid in centroids.iterrows():
        knn_df = knn_stop_region(centroid, pois, k)
        knn_df["lat_sr"] = centroid["latitude"]
        knn_df["lon_sr"] = centroid["longitude"]
        knn_df["sr_id"] = centroid["sr_id"]
        user_knn.append(knn_df)

    return user_knn

def knn_pois_google_places(centroids, pois, k):
    user_knn = []
    for index, centroid in centroids.iterrows():
        knn_df = knn_stop_region_google_places(centroid, pois, k)
        knn_df["lat_sr"] = centroid["latitude"]
        knn_df["lon_sr"] = centroid["longitude"]
        knn_df["sr_id"] = centroid["sr_id"]
        user_knn.append(knn_df)

    return user_knn

def grab_pois_by_stop_region_bounding_box_expand_fixed(pois, stop_regions, expand_value=None):
    limits = box_limits_by_data(stop_regions)

    p1 = {"latitude": limits["max_lat"], "longitude": limits["max_lon"], "point": "p1"}
    p2 = {"latitude": limits["max_lat"], "longitude": limits["min_lon"], "point": "p2"}
    p3 = {"latitude": limits["min_lat"], "longitude": limits["min_lon"], "point": "p3"}
    p4 = {"latitude": limits["min_lat"], "longitude": limits["max_lon"], "point": "p4"}

    box = pd.DataFrame([p1, p2, p3, p4])
    box = box.set_index("point")

    if not expand_value is None:
        box = expand_box_fixed_value(box, expand_value)

    return pois_inside_bounding_box(pois, box)

def expand_box_fixed_value(box, value):
    expanded_box = box.copy()

    expanded_box.ix['p1', 'latitude'] += value
    expanded_box.ix['p1', 'longitude'] += value

    expanded_box.ix['p2', 'latitude'] += value
    expanded_box.ix['p2', 'longitude'] -= value

    expanded_box.ix['p3', 'latitude'] -= value
    expanded_box.ix['p3', 'longitude'] -= value

    expanded_box.ix['p4', 'latitude'] -= value
    expanded_box.ix['p4', 'longitude'] += value

    return expanded_box

def pois_inside_bounding_box(pois, box):
    pois_inside_box = pois[(pois["lat_4326"] >= box["latitude"].min()) &
                           (pois["lat_4326"] <= box["latitude"].max()) &
                           (pois["lon_4326"] >= box["longitude"].min()) &
                           (pois["lon_4326"] <= box["longitude"].max())]

    print("{} pois out of {}".format(len(pois_inside_box), len(pois)))
    return pois_inside_box

def bounding_box(users):
    limits = box_limits(users)

    p1 = {"latitude": limits["max_lat"], "longitude": limits["max_lon"], "point": "p1"}
    p2 = {"latitude": limits["max_lat"], "longitude": limits["min_lon"], "point": "p2"}
    p3 = {"latitude": limits["min_lat"], "longitude": limits["min_lon"], "point": "p3"}
    p4 = {"latitude": limits["min_lat"], "longitude": limits["max_lon"], "point": "p4"}

    box = pd.DataFrame([p1, p2, p3, p4])
    box = box.set_index("point")
    return box


def user_bounding_box(user_id, expand=None):
    box = bounding_box([user_id])

    if expand is None:
        return box

    else:
        box = box.reset_index()
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

        expanded_box = expanded_box.set_index("point")

        return expanded_box

def remove_outliers(data, quantile_threshold=0.05):
    clean_data = data.copy()

    if len(clean_data) == 0:
        return pd.DataFrame()

    lower_lat_value = data["latitude"].quantile(quantile_threshold)
    higher_lat_value = data["latitude"].quantile(1 - quantile_threshold)
    lower_lon_value = data["longitude"].quantile(quantile_threshold)
    higher_lon_value = data["longitude"].quantile(1 - quantile_threshold)

    clean_data = clean_data[
        (clean_data["latitude"] >= lower_lat_value) & (clean_data["latitude"] <= higher_lat_value) & (
                    clean_data["longitude"] >= lower_lon_value) & (clean_data["longitude"] <= higher_lon_value)]

    return clean_data


def infer_close_sr_as_home(home_stop_regions, stop_regions, radius=20, search_tolerance=0.001):
    '''
    Return all Stop Regions that stands inside the given radius for some place Stop Region
    :param place_stop_regions:
    :param stop_regions:
    :param radius:
    :search_tolerance:
    :return:
    '''

    return get_closest_stop_regions(home_stop_regions, stop_regions, radius=radius, search_tolerance=search_tolerance)

def infer_close_sr_as_work(work_stop_regions, stop_regions, radius=10, search_tolerance=0.0005):
    '''
    Return all Stop Regions that stands inside the given radius for some place Stop Region
    :param place_stop_regions:
    :param stop_regions:
    :param radius:
    :search_tolerance:
    :return:
    '''

    return get_closest_stop_regions(work_stop_regions, stop_regions, radius=radius, search_tolerance=search_tolerance)


def get_closest_stop_regions(place_stop_regions, stop_regions, radius, search_tolerance=0.001):
    '''
    Return all Stop Regions that stands inside the given radius for some place Stop Region
    :param place_stop_regions:
    :param stop_regions:
    :param radius:
    :search_tolerance:
    :return:
    '''
    sr_close_to_place = pd.DataFrame()

    for i, stop_region in stop_regions.iterrows():

        min_lats = place_stop_regions["latitude"] - search_tolerance
        max_lats = place_stop_regions["latitude"] + search_tolerance
        min_lons = place_stop_regions["longitude"] - search_tolerance
        max_lons = place_stop_regions["longitude"] + search_tolerance

        use_place_stop_regions = place_stop_regions[(place_stop_regions["latitude"] >= min_lats) &
                                                    (place_stop_regions["latitude"] <= max_lats) &
                                                    (place_stop_regions["longitude"] >= min_lons) &
                                                    (place_stop_regions["longitude"] <= max_lons)]

        for j, use_place_stop_region in use_place_stop_regions.iterrows():

            d = distance_epsg_4326(stop_region["latitude"],
                                   stop_region["longitude"],
                                   use_place_stop_region["latitude"],
                                   use_place_stop_region["longitude"])

            if d <= radius:
                sr_close_to_place = sr_close_to_place.append(stop_region)
                break

    return sr_close_to_place

def slice_geo_data(data, center, search_tolerance):
    min_lats = center.center_lat - search_tolerance
    max_lats = center.center_lat + search_tolerance
    min_lons = center.center_lon - search_tolerance
    max_lons = center.center_lon + search_tolerance

    return data[(data["latitude"] >= min_lats)  & (data["latitude"] <= max_lats) &
                (data["longitude"] >= min_lons) & (data["longitude"] <= max_lons)]

def slice_geo_data2(data, center_lat, center_lon, search_tolerance):
    min_lats = center_lat - search_tolerance
    max_lats = center_lat + search_tolerance
    min_lons = center_lon - search_tolerance
    max_lons = center_lon + search_tolerance

    return data[(data["latitude"] >= min_lats)  & (data["latitude"] <= max_lats) &
                (data["longitude"] >= min_lons) & (data["longitude"] <= max_lons)]


if __name__ == "__main__":
    from src.dao.dbdao import DBDAO
    from src.dao import places_dao
    import os

    for user_id in DBDAO().users_with_places():
        print()
        print("---------------")
        print("user_id: {}".format(user_id))
        sr = places_dao.load_stop_regions_home(user_id, verbose=True)

        dirpath = "outputs/home_inferred/"
        filename = "home_stop_regions_user_{}_v2.csv".format(user_id)

        if os.path.exists(dirpath + filename):
            print("User already computed")
            continue

        home_close_sr = infer_close_sr_as_home(sr["home"], sr["not_home"], radius=20)
        print("{} stop regions close to home".format(len(home_close_sr)))

        home_sr = sr["home"].append(home_close_sr)
        home_sr["sr_id"].rename("sr_id").to_csv(dirpath + filename, header=True, index=False)