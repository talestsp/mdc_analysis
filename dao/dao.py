import mysql.connector
import pandas as pd
from utils import utils, resource_usage

class DAO:
    def __init__(self, credentials_jon=utils.credentials_db()):
        self.cnx = mysql.connector.connect(
            user=credentials_jon['user'],
            password=credentials_jon['password'],
            host=credentials_jon['host'],
            database=credentials_jon['database'])

        self.res_usage = resource_usage.ResourceUsage()

    def records_df(self, userids=[], columns=["db_key", "userid", "tz", "time", "type"]):
        records_df = pd.DataFrame(self.records(userids=userids, select_columns=", ".join(columns)))
        if len(records_df) > 0:
            records_df.columns = columns
        return records_df

    def users_df(self, userids=[], columns=["userid", "phonenumber", "test_user"]):
        users_df = pd.DataFrame(self.users(userids=userids, select_columns=", ".join(columns)))
        if len(users_df) > 0:
            users_df.columns = columns
        return users_df

    def records(self, userids=[], select_columns="*"):
        query = "SELECT %s FROM records;" % (select_columns)

        if len(userids) > 0:
            query = self.selection_match(query=query,
                                         attribute="userid",
                                         values=userids,
                                         logical_conjunction="OR")

        return self.sql_query(query, verbose=True)

    def users(self, userids=[], select_columns="*"):
        query = "SELECT %s FROM users;" % (select_columns)

        if len(userids) > 0:
            query = self.selection_match(query=query,
                                         attribute="userid",
                                         values=userids,
                                         logical_conjunction="OR")

        return self.sql_query(query, verbose=True)

    def sql_query(self, sql_query, verbose=False):
        cursor = self.cnx.cursor()

        if (verbose):
            self.res_usage.start()
            print(sql_query)

        cursor.execute(sql_query)
        data = cursor.fetchall()
        cursor.close()

        if (verbose):
            self.res_usage.check()

        return data

    def selection_match(self, query, attribute, values, logical_conjunction):
        appendix = " WHERE "

        for value in values:
            appendix = appendix + attribute + "=" + str(value) + " " + logical_conjunction + " "

        appendix = appendix[0:len(appendix) - len(logical_conjunction + " ")]

        return query.replace(";", "") + appendix + ";"


    def __del__(self):
        self.cnx.close()



if __name__ == "__main__":
    dao = DAO()
    data = dao.users_df(userids=["6199", "5448", "5462"])
    print(data)

    data = dao.records_df(userids=["5462"])
    print(data)


