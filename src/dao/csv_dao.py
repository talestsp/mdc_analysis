import pandas as pd
import os
import mathimport



from src.utils.time_utils import local_time

DAY_SECONDS = 86400
TEN_SECONDS = 10

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

def load_user_stop_regions(user, columns=None):
    user = str(user)
    stop_regions = []

    if columns is None:
        columns = ["time", "latitude", "longitude", "sr_id"]

    filenames = sorted(os.listdir("outputs/stop_regions/" + user))

    for stop_region_cluster in filenames:
        sr = pd.read_csv("outputs/stop_regions/" + user + "/" + stop_region_cluster)
        sr["sr_id"] = str(user) + "_" + stop_region_cluster.split("_")[1].split(".csv")[0]
        stop_regions.append(sr[columns])

    return stop_regions


def load_user_stop_regions_centroids(user_id):
    import src.utils.geo as geo
    '''
    Retrurn a single pandas.DataFrame containing all Stop Region centroids for the given user
    :param user_id:
    :return:
    '''
    centroids = []
    stop_regions = load_user_stop_regions(user_id)
    for sr in stop_regions:
        sr_id = sr["sr_id"].drop_duplicates().item()

        centroid = geo.cluster_centroid(sr)
        centroid["sr_id"] = sr_id
        centroids.append(centroid)

    return pd.DataFrame(centroids)

def load_sr_distance_to_close_pois(user_id):
    '''
    Return a single pandas.DataFrame with all nearest POIs for each Stop Region
    :param user_id:
    :return:
    '''
    user_sr_knn_path = "outputs/sr_knn/{}/".format(user_id)
    user_srs_knn = pd.DataFrame()

    for filename in os.listdir(user_sr_knn_path):
        sr_knn = pd.read_csv(user_sr_knn_path + filename)
        sr_knn["position"] = sr_knn.index
        user_srs_knn = user_srs_knn.append(sr_knn)

    return user_srs_knn

def load_hot_osm_pois():
    '''
    Return a pandas.DataFrame with all POIs registered
    :return:
    '''
    pois = pd.read_csv("../hot_osm_analysis/outputs/hot_osm_pois_location_mercator_3857.csv")

    pois["lon_4326"] = round(
        pois.apply(lambda row: geo.convert_3857_4326(lat=row["latitude"], lon=row["longitude"])[0], axis=1), 6)

    pois["lat_4326"] = round(
        pois.apply(lambda row: geo.convert_3857_4326(lat=row["latitude"], lon=row["longitude"])[1], axis=1), 6)

    return pois


def user_home_gps():
    pass
