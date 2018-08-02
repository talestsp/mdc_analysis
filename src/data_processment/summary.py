from src.dao import dbdao
from src.entity.record_types import RecordType
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
                                            right_cols=["latitude", "longitude", "horizontal_accuracy",
                                                        "vertical_accuracy"],
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



    def gps_lat_lon_weird():
        #it seems that there are problemas at latitude and longitude data
        #they seem incomplete, no decimal cases
        pass




user_gps_records()