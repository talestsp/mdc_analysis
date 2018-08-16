import pandas as pd
import os

DAY_SECONDS = 86400

def load_user_gps_csv(userid, from_day_n, to_day_n):
    user_data = pd.read_csv("outputs/user_gps/" + str(userid) + '_gps.csv').drop_duplicates().sort_values(by="time")
    min_time = user_data["time"].min()
    use_data_from_time = min_time + DAY_SECONDS * from_day_n
    use_data_to_time = use_data_from_time + to_day_n * DAY_SECONDS

    return user_data[(user_data["time"] >= use_data_from_time) & (user_data["time"] <= use_data_to_time)]


def load_gps_speeds(userid=None):
    if userid:
        return pd.read_csv("outputs/user_gps/speeds/" + str(userid) + "_user_gps_speeds.csv")

    else:
        data = pd.DataFrame()
        for filename in os.listdir("outputs/user_gps/speeds/"):
            if filename.endswith(".csv"):
                data = data.append(pd.read_csv("outputs/user_gps/speeds/" + filename))
        return data