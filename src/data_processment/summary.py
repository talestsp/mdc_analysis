from src.dao import dao


def user_records():
    my_dao = dao.DAO()
    user_df = my_dao.users_df()
    print("")

    for userid in user_df["userid"]:
        records = my_dao.records_df(userids=[userid])
        print(userid, len(records))
        print("")

user_records()