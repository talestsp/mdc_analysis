from src.dao import dbdao
from src.entity.record_types import RecordType
import pandas as pd

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


def user_gps_records(save_to_filepath="outputs/user_gps_records.csv"):
    my_dao = dbdao.DBDAO()
    user_df = my_dao.users_df()

    user_records_list = []
    use_userids = user_df["userid"]

    for userid in use_userids:
        records_df = my_dao.records_df(userids=[userid], record_type=RecordType.GPS.value)
        print(records_df)

user_gps_records()