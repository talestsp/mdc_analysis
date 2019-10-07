from src.data_processment.stop_region import MovingCentroidStopRegionFinder
import pandas as pd
import os


def find_clusters(userids):
    r = 50
    delta_t = 300

    for userid in userids:
        print("USERID:", userid)

        user_clusters_dir = "outputs/stop_regions/" + str(userid)

        if os.path.exists(user_clusters_dir):
            print("User data already processed")
            print()
            continue

        try:
            print("LOADING USER DATA")
            user_data = load_user_gps_csv(userid)
            if len(user_data) == 0:
                print("Empty csv\n")
                continue

            user_data = local_time(user_data)

            if len(user_data) == 0:
                continue

            print("user_data head")
            print(user_data.head())
            print("FINDING STOP REGIONS")
            clusters = MovingCentroidStopRegionFinder(region_radius=r, delta_time=delta_t).find_clusters(user_data,
                                                                                                         verbose=False)
            print(len(clusters), "found")

            if os.path.isdir("outputs/stop_regions/") and not os.path.exists(user_clusters_dir):
                os.mkdir(user_clusters_dir)
            else:
                raise Exception("outputs/stop_regions/ does not exists, check your working dir")

            for i in range(len(clusters)):
                clusters[i].to_csv(user_clusters_dir + "/" + "cluster_" + str(i) + ".csv", index=False)

        except pd.errors.EmptyDataError:
            print("Empty csv")
        print()

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
        use_data_from_time = min_time + 86400 * from_day_n

    if to_day_n is None:
        use_data_to_time = user_data["local_time"].max()
    else:
        use_data_to_time = use_data_from_time + to_day_n * 86400

    user_data = user_data[(user_data["local_time"] >= use_data_from_time) & (user_data["local_time"] <= use_data_to_time)]

    if fill:
        pass

    return user_data

def local_time(data, time_col="time", tz_col="tz"):
    data["local_" + time_col] = data[time_col] + data[tz_col]
    return data