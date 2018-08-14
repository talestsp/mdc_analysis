import pandas as pd

DAY_SECONDS = 86400

def load_user_gps_csv(userid, from_day_n, to_day_n):
    user_data = pd.read_csv("outputs/user_gps/" + str(userid) + '_gps.csv').drop_duplicates().sort_values(by="time")
    min_time = user_data["time"].min()
    use_data_from_time = min_time + DAY_SECONDS * from_day_n
    use_data_to_time = use_data_from_time + to_day_n * DAY_SECONDS

    return user_data[(user_data["time"] >= use_data_from_time) & (user_data["time"] <= use_data_to_time)]