import pandas as pd
import os
import math
import ast
import src.utils.geo as geo
from src.utils.time_utils import local_time
from src.entity.geo_circle import GeoCircle
from src.entity.stop_region import sr_row_to_stop_region


DAY_SECONDS = 86400
TEN_SECONDS = 10
ROUND_LAT_LON = 5

def load_user_gps_csv(userid, from_day_n=None, to_day_n=None, fill=False):
    try:
        user_data = pd.read_csv("outputs/user_gps/" + str(userid) + '_gps.csv')
    except pd.errors.EmptyDataError:
        return pd.DataFrame()

    user_data = local_time(user_data)
    if len(user_data) > 0:
        user_data = user_data.drop_duplicates().sort_values(by="local_time")

    min_time = user_data["local_time"].min()

    if from_day_n is None:
        use_data_from_time = min_time
    else:
        use_data_from_time = min_time + DAY_SECONDS * from_day_n

    if to_day_n is None:
        use_data_to_time = user_data["local_time"].max()
    else:
        use_data_to_time = use_data_from_time + to_day_n * DAY_SECONDS

    user_data = user_data[(user_data["local_time"] >= use_data_from_time) & (user_data["local_time"] <= use_data_to_time)]

    if fill:
        pass

    return user_data

def load_user_gps_time_window(userid, from_local_time, to_local_time):
    user_gps_data = load_user_gps_csv(userid)

    user_gps_data["userid"] = [userid] * len(user_gps_data)
    user_gps_data = local_time(user_gps_data)
    user_gps_data = user_gps_data[["userid", "latitude", "longitude", "tz", "time", "local_time"]].sort_values("local_time")

    user_gps_data = user_gps_data[(user_gps_data["local_time"] >= from_local_time) & (user_gps_data["local_time"] <= to_local_time)]
    return user_gps_data

def fill_data_missing_ts(data, tolerance=20):
    """
    It fills missing rows. Suppose the time difference between two consecutive points are 100 (greater than a tolerance=20)
    so it creates 8 new entries between them. The row values are the same as the first row.
    :param data:
    :return:
    """

    data = local_time(data)

    last_timestamp = data["local_time"].iloc[0]

    for index, current_row in data[1 : len(data) - 1].iterrows():
        current_timestamp = current_row["local_time"]

        if current_timestamp - last_timestamp >= tolerance:
            for n in range( math.trunc((current_timestamp - last_timestamp) / TEN_SECONDS) - 1):
                new_entry_timestamp = last_timestamp + (n+1) * TEN_SECONDS
                new_row = current_row.copy()
                new_row["local_time"] = new_entry_timestamp
                new_row["db_key"] = None
                data = data.append(new_row)

        last_timestamp = current_timestamp

    return data.sort_values(by="local_time")


def load_gps_speeds(userid=None):
    if userid:
        return pd.read_csv("outputs/user_gps/speeds/" + str(userid) + "_user_gps_speeds.csv")
    else:
        data = pd.DataFrame()
        for filename in os.listdir("outputs/user_gps/speeds/"):
            if filename.endswith(".csv"):
                data = data.append(pd.read_csv("outputs/user_gps/speeds/" + filename))
        return data

def list_user_gps_files():
    filenames = []
    for filename in os.listdir("outputs/user_gps/"):
        if filename.endswith("_gps.csv"):
            filenames.append(filename)
    return filenames

def list_stop_region_usernames():
    dirnames = []
    for dirname in os.listdir("outputs/stop_regions/"):
        if os.path.isdir("outputs/stop_regions/" + dirname):
            dirnames.append(dirname)

    return dirnames

def load_stop_region_by_sr_id(user_id, sr_id):
    return pd.read_csv("outputs/stop_regions/{}/cluster_{}.csv".format(user_id, sr_id.split("_")[1]))

def load_user_stop_regions(user, columns=None):
    '''
    Return user stop regions as list of pandas.DataFrame
    :param user:
    :param columns:
    :return:
    '''
    user = str(user)
    stop_regions = []

    if columns is None:
        columns = ["local_time", "latitude", "longitude", "sr_id"]

    filenames = sorted(os.listdir("outputs/stop_regions/" + user))

    for stop_region_cluster in filenames:
        sr = pd.read_csv("outputs/stop_regions/" + user + "/" + stop_region_cluster)
        sr["sr_id"] = str(user) + "_" + stop_region_cluster.split("_")[1].split(".csv")[0]

        stop_regions.append(sr[columns])

    return stop_regions


def load_user_stop_regions_centroids(user_id, tag_stop_regions=True, round_lat_lon=5):
    '''
    Retrurn a single pandas.DataFrame containing all Stop Region centroids for the given user.
    :param user_id:
    :return:
    '''

    try:
        centroids = pd.read_csv("outputs/centroids/{}_centroids.csv".format(user_id))
        centroids["tag"] = centroids["tag"].where((pd.notnull(centroids["tag"])), None)

    except FileNotFoundError:

        centroids = []
        stop_regions = load_user_stop_regions(user_id)

        if tag_stop_regions:
            home_sr_ids = load_home_inferred_sr_ids(user_id)
            work_sr_ids = load_work_inferred_sr_ids(user_id)

        for sr in stop_regions:
            if len(sr) == 0:
                continue
            sr_id = sr["sr_id"].drop_duplicates().item()
            start_time = sr["local_time"].min()
            end_time = sr["local_time"].max()
            centroid = geo.cluster_centroid(sr)
            centroid["sr_id"] = sr_id
            centroid["user_id"] = user_id
            centroid["local_start_time"] = start_time
            centroid["local_end_time"] = end_time

            if tag_stop_regions:
                centroid['tag'] = ''
                if sr_id in (home_sr_ids):
                    centroid['tag'] = "HOME" + ","
                if sr_id in (work_sr_ids):
                    centroid['tag'] = centroid['tag'] + "WORK" + ","

                centroid['tag'] = centroid['tag'][0 : len(centroid['tag']) - 1]

                if centroid['tag'] == '':
                    centroid['tag'] = None


            centroids.append(centroid)

        centroids = pd.DataFrame(centroids)

        if not round_lat_lon is None:
            centroids['latitude'] = centroids['latitude'].apply(lambda value : round(value, round_lat_lon))
            centroids['longitude'] = centroids['longitude'].apply(lambda value : round(value, round_lat_lon))

    return centroids

def load_sr_distance_to_close_pois(user_id):
    '''
    Return a single pandas.DataFrame with all nearest POIs for each Stop Region
    :param user_id:
    :return:
    '''
    user_sr_knn_path = "outputs/hot_osm_sr_knn/{}/".format(user_id)
    user_srs_knn = pd.DataFrame()
    for filename in os.listdir(user_sr_knn_path):
        sr_knn = pd.read_csv(user_sr_knn_path + filename)
        sr_knn["position"] = sr_knn.index
        user_srs_knn = user_srs_knn.append(sr_knn)

    return user_srs_knn

def load_sr_distance_to_close_pois_google_places(user_id):
    '''
    Return a single pandas.DataFrame with all nearest POIs for each Stop Region
    :param user_id:
    :return:
    '''
    user_sr_knn_path = "outputs/google_places_sr_knn/{}/".format(user_id)
    user_srs_knn = pd.DataFrame()
    for filename in os.listdir(user_sr_knn_path):
        sr_knn = pd.read_csv(user_sr_knn_path + filename)
        sr_knn = sr_knn.sort_values("distance")
        sr_knn["position"] = sr_knn.index
        user_srs_knn = user_srs_knn.append(sr_knn)

    return user_srs_knn

def filter_valid_amenities(pois):
    return pois[pois["amenity"].isna() == False]

def filter_valid_pois(pois):
    columns = ["amenity", "leisure", "tourism", "shop", "historic", "sport", "building", "office",
               "access", "religion", "bicycle", "public_transport", "power", "natural",
               "man_made", "railway", "military", "place", "aerialway", "waterway"]

    valid_pois = pois[pois[columns].any(axis=1)].copy()

    valid_pois["building_+_religion"] = valid_pois["building"] + " + " + valid_pois["religion"]

    del valid_pois["religion"]

    return valid_pois

def load_hot_osm_pois(valid_pois=False):
    '''
    Return a pandas.DataFrame with all POIs registered
    :return:
    '''
    pois = pd.read_csv("../hot_osm_analysis/outputs/planet_osm_point_full.csv")

    if valid_pois:
        pois = filter_valid_pois(pois)
    return pois


def load_all_users_stop_regions_centroids(unique_sr=False, verbose=False, round_lat_lon=5):
    stop_regions = pd.DataFrame()

    for user_id in list_stop_region_usernames():
        stop_regions = stop_regions.append(load_user_stop_regions_centroids(user_id, round_lat_lon=round_lat_lon))
        if verbose:
            print("User {} data loaded".format(user_id))

    print("All Stop Regions:    {}".format(len(stop_regions)))

    if unique_sr:
        stop_regions = unique_stop_regions(stop_regions)
        print("Unique Stop Regions:    {}".format(len(stop_regions)))

    return stop_regions

def unique_stop_regions(sr_data, on_cols=['latitude', 'longitude']):
    unique_sr = sr_data.drop_duplicates(subset=on_cols, keep="first")["sr_id"].tolist()
    return sr_data[sr_data["sr_id"].isin(unique_sr)]

def load_home_inferred_sr_ids(user_id):
    '''
    Home places using geo.infer_close_sr_as_home
    :param user_id:
    :return:
    '''
    try:
        data = pd.read_csv("outputs/home_inferred/home_stop_regions_user_{}_v2.csv".format(user_id))['sr_id'].tolist()
        return data
    except FileNotFoundError:
        return []

def load_work_inferred_sr_ids(user_id):
    '''
    Work places using geo.infer_close_sr_as_home
    :param user_id:
    :return:
    '''
    try:
        data = pd.read_csv("outputs/work_inferred/work_stop_regions_user_{}_v2.csv".format(user_id))['sr_id'].tolist()
        return data
    except FileNotFoundError:
        return []

def load_home_inferred_sr(user_id):
    '''
    Home places using geo.infer_close_sr_as_home
    :param user_id:
    :return:
    '''
    home_sr_ids = pd.read_csv("outputs/home_inferred/home_stop_regions_user_{}_v2.csv".format(user_id))
    stop_regions = load_user_stop_regions_centroids(user_id)
    return stop_regions[stop_regions["sr_id"].isin(home_sr_ids)]

def load_work_inferred_sr(user_id):
    '''
    Work places using geo.infer_close_sr_as_home
    :param user_id:
    :return:
    '''
    work_sr_ids = pd.read_csv("outputs/home_inferred/work_stop_regions_user_{}_v2.csv".format(user_id))
    stop_regions = load_user_stop_regions_centroids(user_id)
    return stop_regions[stop_regions["sr_id"].isin(work_sr_ids)]

def save_request_circles(request_circle_list, radius, search_tolerance):
    rc_ids = []
    center_lats = []
    center_lons = []
    radius_list = []
    stop_regions_inside = []

    for request_circle in request_circle_list:
        rc_ids.append(request_circle.id)
        center_lats.append(request_circle.center_lat)
        center_lons.append(request_circle.center_lon)
        radius_list.append(request_circle.radius_m)

        stop_regions_ids = []
        for index, sr in request_circle.sr.iterrows():
            stop_regions_ids.append(sr["sr_id"])
        stop_regions_inside.append(stop_regions_ids)

    request_circles = pd.DataFrame()
    request_circles["rc_id"] = rc_ids
    request_circles["latitude"] = center_lats
    request_circles["longitude"] = center_lons
    request_circles["radius_m"] = radius_list
    request_circles["search_tolerance"] = [search_tolerance] * len(request_circles["radius_m"])
    request_circles["sr_ids"] = stop_regions_inside

    request_circles.to_csv("outputs/request_circles/rerquest_circles_{}m.csv".format(radius))

def load_request_circles(request_radius):
    request_df = load_request_circles_df(request_radius)
    stop_regions = load_all_users_stop_regions_centroids()

    request_circles = []

    for index, row in request_df.iterrows():
        geo_c = GeoCircle(row["latitude"], row["longitude"], row["radius_m"], id=row["rc_id"])
        geo_c.put_data(stop_regions[stop_regions["sr_id"].isin(geo_c["sr_ids"])])

        request_circles.append(geo_c)

    return request_circles

def load_request_circles_df(request_radius):
    data = pd.read_csv("outputs/request_circles/rerquest_circles_{}m.csv".format(request_radius))
    if "Unnamed: 0" in data.columns.tolist():
        del data["Unnamed: 0"]

        data["sr_ids"] = data["sr_ids"].apply(ast.literal_eval)
    return data

def load_knn_pois_by_stop_region(stop_region):
    try:
        user_sr_knn_path = "outputs/google_places_sr_knn/{}/".format(stop_region.user_id)
        sr_knn = pd.read_csv(user_sr_knn_path + "sr_" + stop_region.sr_id + "_knn.csv")
    except FileNotFoundError as e:
        sr_knn = load_equivalent_stop_region(stop_region)
        sr_knn = sr_knn.drop_duplicates(subset="place_id")

    sr_knn = sr_knn.sort_values("distance")
    sr_knn["position"] = sr_knn.index
    return sr_knn


def load_equivalent_stop_region(stop_region):
    user_sr_knns = load_sr_distance_to_close_pois_google_places(stop_region.user_id)

    user_sr_knns["lat_sr"] = user_sr_knns["lat_sr"].apply(lambda lat: round(lat, ROUND_LAT_LON))
    user_sr_knns["lon_sr"] = user_sr_knns["lon_sr"].apply(lambda lon: round(lon, ROUND_LAT_LON))

    return user_sr_knns[(user_sr_knns["lat_sr"] == stop_region.centroid_lat) & (user_sr_knns["lon_sr"] == stop_region.centroid_lon)]

def stop_region_sequence(user_id):
    sr = load_user_stop_regions_centroids(user_id).sort_values("local_start_time")
    sr_sequence = sr.apply(sr_row_to_stop_region, axis=1).tolist()
    return sr_sequence

if __name__ == "__main__":
    d200 = load_request_circles_df(200)




