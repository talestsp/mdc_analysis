from dao import dao

def user_records():
    user_df = dao.DAO().users_df()

    print(user_df["test_user"].value_counts())

    # for userid in user_df["userid"]:
    #     dao.DAO().users_df()