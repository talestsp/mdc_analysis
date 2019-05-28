import pandas as pd

from src.dao import csv_dao, dbdao
from src.utils  import time_utils
from src.utils import geo

def load_users_gps_data(userids,
                        cols=["userid", "latitude", "longitude", "tz", "time", "local_time", "horizontal_accuracy",
                              "horizontal_dop", "speed"]):
    df = pd.DataFrame()

    for userid in userids:
        df = df.append(load_user_gps_data(userid))

    df = time_utils.local_time(df)

    if cols != "*":
        df = df[cols]

    df = df.sort_values("local_time")

    return df


def load_user_gps_data(userid,
                       cols=["userid", "latitude", "longitude", "tz", "time", "local_time", "horizontal_accuracy",
                             "horizontal_dop", "speed"]):

    user_gps_data = csv_dao.load_user_gps_csv(userid)
    user_gps_data["userid"] = [userid] * len(user_gps_data)

    if cols != "*":
        user_gps_data = user_gps_data[cols]

    user_gps_data = user_gps_data.sort_values("local_time")

    return user_gps_data

def places_work(userid, do_remove_outliers=True):
    '''
    Returns intervals that the user stated as work time
    :userid:
    :return:
    '''
    user_gps_data = load_user_gps_data(userid)
    if len(dbdao.DBDAO().places_work_df(userid=userid)) == 0:
        return pd.DataFrame()

    work_visit_data = dbdao.DBDAO().places_work_df(userid=userid).sort_values("time_start")
    work_gps_data = places(work_visit_data, user_gps_data)

    if do_remove_outliers:
        return geo.remove_outliers(work_gps_data)

    return work_gps_data


def places(place_label_visit_data, user_gps_data):
    place_label_visit_data = time_utils.local_time(place_label_visit_data, time_col="time_start", tz_col="tz_start")
    place_label_visit_data = time_utils.local_time(place_label_visit_data, time_col="time_end", tz_col="tz_end")

    user_visit_locations = pd.DataFrame()

    for index, row in place_label_visit_data.iterrows():
        user_visit_locations = user_visit_locations.append(user_gps_data[(user_gps_data["local_time"] >= row[
            "local_time_start"]) & (user_gps_data["local_time"] <= row["local_time_end"])])

    return user_visit_locations


def places_home(userid, do_remove_outliers=False):
    '''
    Returns a list of places that matches the time the user informed as being at home.
    :param userid:
    :return:
    '''
    user_gps_data = load_user_gps_data(userid)
    if len(dbdao.DBDAO().places_home_df(userid=userid)) == 0:
        return pd.DataFrame()

    home_visit_data = dbdao.DBDAO().places_home_df(userid=userid).sort_values("time_start")
    home_gps_data = places(home_visit_data, user_gps_data)

    if do_remove_outliers:
        return geo.remove_outliers(home_gps_data)

    return home_gps_data


def places(place_label_visit_data, user_gps_data):
    '''
    Returns a pandas.DataFrame that matches the time of the informed places the user have been with GPS points.
    This match is based on local_time.
    :param place_label_visit_data:
    :param user_gps_data:
    :return:
    '''
    place_label_visit_data = time_utils.local_time(place_label_visit_data, time_col="time_start", tz_col="tz_start")
    place_label_visit_data = time_utils.local_time(place_label_visit_data, time_col="time_end", tz_col="tz_end")

    user_visit_locations = pd.DataFrame()

    for index, row in place_label_visit_data.iterrows():
        user_visit_locations = user_visit_locations.append(user_gps_data[(user_gps_data["local_time"] >= row[
            "local_time_start"]) & (user_gps_data["local_time"] <= row["local_time_end"])])

    return user_visit_locations


def stop_regions_home(home_points, stop_regions):
    '''
    Match Stop Regions that contains gps points stated by the user as home points.
    :param home_points:
    :param stop_regions:
    :return:
    '''
    if len(home_points) == 0:
        return []

    home_stop_regions = []

    for index_sr, sr in stop_regions.iterrows():
        points_match = home_points[
            (home_points["local_time"] > sr["local_start_time"]) & (home_points["local_time"] < sr["local_end_time"])]

        if len(points_match) > 0:
            home_stop_regions.append(sr["sr_id"])

    return home_stop_regions

def stop_regions_work(work_points, stop_regions):
    '''
    Match Stop Regions that contains gps points stated by the user as work points.
    :param home_points:
    :param stop_regions:
    :return:
    '''
    if len(work_points) == 0:
        return []

    work_stop_regions = []

    for index_sr, sr in stop_regions.iterrows():
        points_match = work_points[
            (work_points["local_time"] > sr["local_start_time"]) & (work_points["local_time"] < sr["local_end_time"])]

        if len(points_match) > 0:
            work_stop_regions.append(sr["sr_id"])

    return work_stop_regions

def load_stop_regions_home(user_id, verbose=False):
    print("My Warning!")
    print("Try to use csv_dao.load_user_stop_regions_centroids")
    user_sr = csv_dao.load_user_stop_regions_centroids(user_id)

    if verbose:
        print("{} stop regions".format(len(user_sr)))
        print()

    home_points = places_home(user_id, do_remove_outliers=True)

    sr_ids = stop_regions_home(home_points, user_sr)

    home_sr = user_sr[user_sr["sr_id"].isin(sr_ids)]
    not_home_sr = user_sr[~user_sr["sr_id"].isin(sr_ids)]

    if verbose:
        print("{} stop regions HOME".format(len(home_sr)))
        print("{} stop regions NOT HOME".format(len(not_home_sr)))

    return {"home": home_sr, "not_home" : not_home_sr}


def load_stop_regions_work(user_id, verbose=False):
    print("My Warning!")
    print("Try to use csv_dao.load_user_stop_regions_centroids")
    user_sr = csv_dao.load_user_stop_regions_centroids(user_id)

    if verbose:
        print("{} stop regions".format(len(user_sr)))
        print()

    work_points = places_work(user_id, do_remove_outliers=True)

    sr_ids = stop_regions_work(work_points, user_sr)

    work_sr = user_sr[user_sr["sr_id"].isin(sr_ids)]
    not_work_sr = user_sr[~user_sr["sr_id"].isin(sr_ids)]

    if verbose:
        print("{} stop regions WORK".format(len(work_sr)))
        print("{} stop regions NOT WORK".format(len(not_work_sr)))

    return {"work": work_sr, "not_work" : not_work_sr}




