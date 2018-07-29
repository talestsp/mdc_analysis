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

    def records(self):
        query = "SELECT * FROM records;"
        return self.sql_query(query, verbose=True)

    def users(self):
        query = "SELECT * FROM users;"
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
    dao.records()



