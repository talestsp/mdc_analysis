import pandas as pd

from src.dao import csv_dao, dbdao
from src.utils  import time_utils

def load_users_gps_data(userids,
                        cols=["userid", "latitude", "longitude", "tz", "time", "local_time", "horizontal_accuracy",
                              "horizontal_dop", "speed"]):
    df = pd.DataFrame()
    for userid in userids:
        user_gps_df = csv_dao.load_user_gps_csv(userid)
        user_gps_df["userid"] = [userid] * len(user_gps_df)
        df = df.append(user_gps_df)

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

def places_home(userid):
    '''
    Returns intervals that the user stated as home time
    :userid:
    :return:
    '''
    user_gps_data = load_user_gps_data(userid)
    if len(dbdao.DBDAO().places_home_df(userid=userid)) == 0:
        return pd.DataFrame()

    home_visit_data = dbdao.DBDAO().places_home_df(userid=userid).sort_values("time_start")
    return places(home_visit_data, user_gps_data)


def places_work(userid):
    '''
    Returns intervals that the user stated as work time
    :userid:
    :return:
    '''
    user_gps_data = load_user_gps_data(userid)
    if len(dbdao.DBDAO().places_work_df(userid=userid)) == 0:
        return pd.DataFrame()

    work_visit_data = dbdao.DBDAO().places_work_df(userid=userid).sort_values("time_start")
    return places(work_visit_data, user_gps_data)


def places(place_label_visit_data, user_gps_data):
    place_label_visit_data = time_utils.local_time(place_label_visit_data, time_col="time_start", tz_col="tz_start")
    place_label_visit_data = time_utils.local_time(place_label_visit_data, time_col="time_end", tz_col="tz_end")

    user_visit_locations = pd.DataFrame()

    for index, row in place_label_visit_data.iterrows():
        user_visit_locations = user_visit_locations.append(user_gps_data[(user_gps_data["local_time"] >= row[
            "local_time_start"]) & (user_gps_data["local_time"] <= row["local_time_end"])])

    return user_visit_locations
