from src.data_processment.stop_region import MovingCentroidStopRegionFinder
from src.dao.csv_dao import load_user_gps_csv
from src.dao.dbdao import DBDAO
from src.utils.time_utils import local_time
import pandas as pd
import gc
import os

my_dao = DBDAO()
user_df = my_dao.users_df()
userids = user_df["userid"]
my_dao = None
gc.collect()

r = 50
delta_t = 300

for userid in userids[1:]:
    print("USERID:", userid)

    user_clusters_dir = "outputs/stop_regions/" + str(userid)

    if os.path.exists(user_clusters_dir):
        print("User data already processed")
        print()
        continue

    try:
        print("LOADING USER DATA")
        user_data = local_time(load_user_gps_csv(userid))
        if len (user_data) == 0:
            continue

        print("user_data")
        print(user_data)
        print("FINDING STOP REGIONS")
        clusters = MovingCentroidStopRegionFinder(region_radius=r, delta_time=delta_t).find_clusters(user_data, verbose=False)
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