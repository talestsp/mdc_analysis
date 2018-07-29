import mysql.connector
import pandas as pd
from utils import utils, resource_usage

class DAO:
    class __DAO:
        def __init__(self, credentials_jon):
            self.cnx = mysql.connector.connect(
                user=credentials_jon['user'],
                password=credentials_jon['password'],
                host=credentials_jon['host'],
                database=credentials_jon['database'])

            self.res_usage = resource_usage.ResourceUsage()

    instance = None
    def __init__(self, credentials_jon):
        if not DAO.instance:
            DAO.instance = DAO.__DAO(credentials_jon)
        else:
            DAO.instance.credentials_jon = credentials_jon

    def records_df(self, columns=["db_key", "userid", "tz", "time", "type"]):
        records_df = pd.DataFrame(self.records(select_columns=", ".join(columns)))
        records_df.columns = columns
        return records_df

    def users_df(self, userids=[], columns=["userid", "phonenumber", "test_user"]):
        users_df = pd.DataFrame(self.users(userids=userids, select_columns=", ".join(columns)))
        users_df.columns = columns
        return users_df

    def records(self, select_columns="*"):
        query = "SELECT %s FROM records;" % (select_columns)
        return self.sql_query(query, verbose=True)

    def users(self, userids=[], select_columns="*"):
        query = "SELECT %s FROM users;" % (select_columns)

        if len(userids) > 0:
            query = self.selection_match(query = query,
                                         attribute="userid",
                                         values=userids,
                                         logical_conjunction="OR")

        print(query)
        return self.sql_query(query, verbose=True)

    def sql_query(self, sql_query, verbose=False):
        cursor = self.instance.cnx.cursor()

        if (verbose):
            self.instance.res_usage.start()

        cursor.execute(sql_query)
        data = cursor.fetchall()
        cursor.close()

        if (verbose):
            self.instance.res_usage.check()

        return data

    def selection_match(self, query, attribute, values, logical_conjunction):
        appendix = " WHERE "

        for value in values:
            appendix = appendix + attribute + "=" + value + " " + logical_conjunction + " "

        appendix = appendix[0:len(appendix) - len(logical_conjunction + " ")]

        return query.replace(";", "") + appendix + ";"


    def __del__(self):
        self.instance.cnx.close()



if __name__ == "__main__":
    dao = DAO(utils.credentials_db())
    data = dao.users(userids=["6199", "6214", "6272"])
    print(data)


