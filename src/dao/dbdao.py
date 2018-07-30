import mysql.connector
import pandas as pd
from src.utils import utils, resource_usage


class DBDAO:
    def __init__(self, credentials_jon=utils.credentials_db()):
        self.cnx = mysql.connector.connect(
            user=credentials_jon['user'],
            password=credentials_jon['password'],
            host=credentials_jon['host'],
            database=credentials_jon['database'])

        self.res_usage = resource_usage.ResourceUsage()

    def records_df(self, userids=[], columns=["db_key", "userid", "tz", "time", "type"]):
        data = self.records(userids=userids, select_columns=", ".join(columns))
        return self.to_df(data, columns)

    def users_df(self, userids=[], columns=["userid", "phonenumber", "test_user"]):
        data = self.users(userids=userids, select_columns=", ".join(columns))
        return self.to_df(data, columns)

    def places_df(self, userids=[], columns=["userid", "placeid", "place_label", "with_family", "with_close_friends", "with_friends", "with_colleagues_acquaintances", "with_incidental"]):
        data = self.places(userids=userids, select_columns=", ".join(columns))
        return self.to_df(data, columns)

    def to_df(self, data, columns):
        data = pd.DataFrame(data)
        if len(data) > 0:
            data.columns = columns

        return data

    def places_df(self, userids=[], columns=["userid", "placeid", "place_label", "with_family", "with_close_friends", "with_friends", "with_colleagues_acquaintances", "with_incidental"]):
        data = self.places(userids=userids, select_columns=", ".join(columns))
        return self.to_df(data, columns)

    def to_df(self, data, columns):
        data = pd.DataFrame(data)
        if len(data) > 0:
            data.columns = columns

        return data

    def records(self, userids=[], select_columns="*"):
        query = "SELECT %s FROM records;" % (select_columns)

        if len(userids) > 0:
            query = self.selection_match(query=query,
                                         attribute="userid",
                                         values=userids,
                                         logical_conjunction="OR")

        return self.sql_query(query, verbose=False)

    def users(self, userids=[], select_columns="*"):
        query = "SELECT %s FROM users;" % (select_columns)

        if len(userids) > 0:
            query = self.selection_match(query=query,
                                         attribute="userid",
                                         values=userids,
                                         logical_conjunction="OR")

        return self.sql_query(query, verbose=False)

    def places(self, userids=[], select_columns="*"):
        query = "SELECT %s FROM places;" % (select_columns)

        if len(userids) > 0:
            query = self.selection_match(query=query,
                                         attribute="userid",
                                         values=userids,
                                         logical_conjunction="OR")

        return self.sql_query(query, verbose=False)

    def gps(self, dbkeys=[], select_columns=["time", "latitude", "longitude", "altitude", "speed", "horizontal_accuracy", "horizontal_dop", "vertical_accuracy", "vertical_dop", "speed_accuracy", "time_since_gps_boot"]):
        query = "SELECT %s FROM gps;" % (select_columns)

        if len(dbkeys) > 0:
            query = self.selection_match(query, "dbkey", dbkeys, "OR")

        return self.sql_query(query, verbose=False)


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
    dao = DBDAO()
    data = dao.users_df(userids=["6199", "5448", "5462"])
    print(data)

    data = dao.records_df(userids=["5462"])
    print(data)


    data = dao.places_df()
    print(data)


