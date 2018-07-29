import mysql.connector
import pandas as pd
from utils import utils, resource_usage

class DAO:

    def __init__(self, credentials_jon):
        self.cnx = mysql.connector.connect(
                                     user=credentials_jon['user'],
                                     password=credentials_jon['password'],
                                     host=credentials_jon['host'],
                                     database=credentials_jon['database'])

        self.res_usage = resource_usage.ResourceUsage()

        print(self.cnx)

    def records_df(self, columns=["db_key", "userid", "tz", "time", "type"]):
        records_df = pd.DataFrame(self.records(", ".join(columns)))
        records_df.columns = columns
        return records_df

    def users_df(self, columns=["userid", "phonenumber", "test_user"]):
        users_df = pd.DataFrame(self.users(", ".join(columns)))
        users_df.columns = columns
        return users_df

    def records(self, select_columns="*"):
        query = "SELECT %s FROM records;" % (select_columns)
        return self.sql_query(query, verbose=True)

    def users(self, select_columns="*"):
        query = "SELECT %s FROM users;" % (select_columns)

        return self.sql_query(query, verbose=True)

    def sql_query(self, sql_query, verbose=False):
        cursor = self.cnx.cursor()

        if (verbose):
            self.res_usage.start()

        cursor.execute(sql_query)
        data = cursor.fetchall()

        if (verbose):
            self.res_usage.check()

        return data



if __name__ == "__main__":
    dao = DAO(utils.credentials_db())
    dao.users()



