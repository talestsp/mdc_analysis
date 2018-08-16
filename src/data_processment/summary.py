from src.dao import dbdao
from src.entity.record_types import RecordType
from src.utils.stats import quantiles
from src.utils.geo import haversine_vectorized
import pandas as pd
import os

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

def user_total_records(save_to_filepath="outputs/user_total_records.csv"):
    my_dao = dbdao.DBDAO()
    user_df = my_dao.users_df()

    try:
        already_computed = pd.read_csv(save_to_filepath)

        user_records_list = already_computed.to_dict(orient="records")
        use_userids = set(user_df["userid"]) - set(already_computed["userid"])
    except FileNotFoundError:
        user_records_list = []
        use_userids = user_df["userid"]

    for userid in use_userids:
        records = my_dao.records_df(userids=[userid])
        user_records_list.append({"userid": userid, "n_records": len(records)})
        pd.DataFrame(user_records_list).to_csv(save_to_filepath, index=False)

        print("userid:", userid, " - ", len(user_records_list), "out of", len(user_df))
        print("n_records:", len(records))
        print("")


def user_gps_records():
    my_dao = dbdao.DBDAO()
    user_df = my_dao.users_df()
    my_dao.close_connection()
    count = 0

    for userid in user_df["userid"]:
        count += 1
        my_dao = dbdao.DBDAO()
        print("\n")
        print("USERID:", userid)

        if not os.path.isfile("outputs/user_gps/" + str(userid) + "_gps.csv"):
            my_dao = dbdao.DBDAO()
            result = my_dao.records_join_df(join_to_table=RecordType.GPS.value,
                                            right_cols=["latitude", "longitude", "speed", "horizontal_accuracy",
                                                        "vertical_accuracy", "speed_accuracy"],
                                            userids=[userid], verbose=True)
            result.to_csv("outputs/user_gps/" + str(userid) + "_gps.csv", index=False)

            if len(result) > 5:
                print(result.sample(5))
            my_dao.close_connection()

        if not os.path.isfile("outputs/user_gpswlan/" + str(userid) + "_gpswlan.csv"):
            my_dao = dbdao.DBDAO()
            result = my_dao.records_join_df(join_to_table=RecordType.GPSWLAN.value,
                                            right_cols=["latitude", "longitude"],
                                            userids=[userid], verbose=True)
            result.to_csv("outputs/user_gpswlan/" + str(userid) + "_gpswlan.csv", index=False)

            if len(result) > 5:
                print(result.sample(5))
            my_dao.close_connection()


        if not os.path.isfile("outputs/user_accel/" + str(userid) + "_accel.csv"):
            my_dao = dbdao.DBDAO()
            result = my_dao.records_join_df(join_to_table=RecordType.ACCEL.value,
                                            right_cols=["start", "stop", "avdelt", "data"],
                                            userids=[userid], verbose=True)
            result.to_csv("outputs/user_accel/" + str(userid) + "_accel.csv", index=False)

            if len(result) > 5:
                print(result.sample(5))
            my_dao.close_connection()

        print("Instances:", count, "out of", len(user_df["userid"]))
        print("--")



def time_resolution_gps(userids=None):
    if userids is None:
        my_dao = dbdao.DBDAO()
        user_df = my_dao.users_df()
        userids = user_df["userid"]
        my_dao.close_connection()

    time_diffs_list_dict = []

    for userid in userids:
        print(userid)
        try:
            user_gps_df = pd.read_csv("outputs/user_gps/" + str(userid) + "_gps.csv")
            user_gps_df = user_gps_df.sort_values(by="time")
            user_time = user_gps_df["time"][1:len(user_gps_df)].reset_index(drop=True)
            user_time_prev = user_gps_df["time"][0:len(user_gps_df) - 1].reset_index(drop=True)

            diff = user_time - user_time_prev

            time_diffs_list_dict.append({"userid": userid, "time_diff_percentiles": quantiles(diff)})

        except pd.errors.EmptyDataError:
            print("Empty CSV")
        print("")

    pd.DataFrame(time_diffs_list_dict).to_csv("outputs/time_resolution_gps.csv", index=False)


def speed_gps(userids=None):
    if userids is None:
        my_dao = dbdao.DBDAO()
        user_df = my_dao.users_df()
        userids = user_df["userid"]
        my_dao.close_connection()

    speeds_list_dict = []

    for userid in userids:
        print(userid)
        try:
            user_gps_df = pd.read_csv("outputs/user_gps/" + str(userid) + "_gps.csv")
            user_gps_df = user_gps_df.sort_values(by="time").drop_duplicates()

            sp = quantiles(user_gps_df["speed"])
            sp["userid"] = userid

            if user_gps_df["speed"].count() > 0:
                n = len(user_gps_df["speed"])
                valid_values = float(user_gps_df["speed"].count())
                sp["nan_proportion"] = (n - valid_values) / (n)
            else:
                sp["nan_proportion"] = 0

            speeds_list_dict.append(sp)

        except pd.errors.EmptyDataError:
            print("Empty CSV")
        print("")

    pd.DataFrame(speeds_list_dict).to_csv("outputs/speed_gps.csv", index=False)

    print(pd.DataFrame(speeds_list_dict).describe())

def speed_nan(userids=None):
    if userids is None:
        my_dao = dbdao.DBDAO()
        user_df = my_dao.users_df()
        userids = user_df["userid"]
        my_dao.close_connection()

    for userid in userids:
        print(userid)
        try:
            user_gps_df = pd.read_csv("outputs/user_gps/" + str(userid) + "_gps.csv")
            user_gps_df = user_gps_df.sort_values(by="time").drop_duplicates().reset_index(drop=True)

            nan_indexes = user_gps_df[user_gps_df["speed"].isnull()].index.tolist()
            nan_index_data_list = []

            for nan_index in nan_indexes:
                if nan_index > 0:
                    prev_loc = user_gps_df.loc[nan_index - 1][["latitude", "longitude", "time"]]
                    loc = user_gps_df.loc[nan_index][["latitude", "longitude", "time"]]
                    dS = haversine_vectorized(loc["longitude"], loc["latitude"], prev_loc["longitude"], prev_loc["latitude"])
                    dT = loc["time"] - prev_loc["time"]

                    nan_index_data_list.append({"userid": userid, "current_time": loc["time"], "dS": dS, "dT": dT, "speed_valid": 0, "lon": loc["longitude"], "lat": loc["latitude"], "prev_lon": prev_loc["longitude"], "prev_lat": prev_loc["latitude"]})

            not_nan_indexes = set(user_gps_df.index.tolist()) - set(nan_indexes)
            not_nan_index_data_list = []

            for not_nan_index in not_nan_indexes:
                if not_nan_index > 0:
                    prev_loc = user_gps_df.loc[not_nan_index - 1][["latitude", "longitude", "time"]]
                    loc = user_gps_df.loc[not_nan_index][["latitude", "longitude", "time"]]
                    dS = haversine_vectorized(loc["longitude"], loc["latitude"], prev_loc["longitude"], prev_loc["latitude"])
                    dT = loc["time"] - prev_loc["time"]

                    not_nan_index_data_list.append({"userid": userid, "current_time": loc["time"], "dS": dS, "dT": dT, "speed_valid": 1, "lon": loc["longitude"], "lat": loc["latitude"], "prev_lon": prev_loc["longitude"], "prev_lat": prev_loc["latitude"]})


            pd.DataFrame(nan_index_data_list + not_nan_index_data_list).to_csv("outputs/user_gps/speeds/" + str(userid) + "_user_gps_speeds.csv", index=False)


        except pd.errors.EmptyDataError:
            print("Empty CSV")
        print("")




speed_nan()
