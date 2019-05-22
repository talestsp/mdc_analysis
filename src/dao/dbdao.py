import mysql.connector
import pandas as pd
from src.utils import others, resource_usage

RECORDS_COLUMNS = ["db_key", "userid", "tz", "time", "type"]
USERS_COLUMNS = ["userid", "phonenumber", "test_user"]
GPS_COLUMNS = ["db_key", "time", "latitude", "longitude", "altitude", "speed", "horizontal_accuracy", "horizontal_dop", "vertical_accuracy", "vertical_dop", "speed_accuracy", "time_since_gps_boot"]
GPSWLAN_COLUMNS = ["db_key", "latitude", "longitude", "mac"]
ACCEL_COLUMNS = ["db_key", "start", "stop", "avdelt", "data"]
PLACES_COLUMNS = ["userid", "placeid", "place_label", "with_family", "with_close_friends", "with_friends", "with_colleagues_acquaintances", "with_incidental"]
PLACES_HOME_COLUMNS = ["userid", "place_label", "placeid", "time_start", "time_end", "tz_start", "tz_end", "trusted_start", "trusted_end", "trusted_transition"]
PLACES_WORK_COLUMNS = ["userid", "place_label", "placeid", "time_start", "time_end", "tz_start", "tz_end", "trusted_start", "trusted_end", "trusted_transition"]

class DBDAO:
    def __init__(self, credentials_jon=others.credentials_db()):
        self.cnx = mysql.connector.connect(
            user=credentials_jon['user'],
            password=credentials_jon['password'],
            host=credentials_jon['host'],
            database=credentials_jon['database'])

        self.res_usage = resource_usage.ResourceUsage()

    def records_df(self, userids=None, record_type=None, columns=RECORDS_COLUMNS, verbose=False):
        data = self.records(userids=userids, record_type=record_type, select_columns=", ".join(columns), verbose=verbose)
        return self.to_df(data, columns)

    def users_df(self, userids=None, drop_test_users=True, columns=USERS_COLUMNS, verbose=False):
        data = self.users(userids=userids, drop_test_users=drop_test_users, select_columns=", ".join(columns), verbose=verbose)
        return self.to_df(data, columns)

    def places_df(self, userids=None, columns=PLACES_COLUMNS, verbose=False):
        data = self.places(userids=userids, select_columns=", ".join(columns), verbose=verbose)
        return self.to_df(data, columns)

    def records_join_df(self, join_to_table, right_cols, how="INNER", record_cols=RECORDS_COLUMNS, userids=None, verbose=False):
        data = self.records_join(join_to_table, right_cols, how, record_cols, userids, verbose)
        return self.to_df(data, right_cols + record_cols)

    #def places_df(self):
    #    data = self.places()
    #    return self.to_df(data, PLACES_COLUMNS)

    def places_home_df(self, userid, trusted_times=True, verbose=False):
        data = self.places_label(userid, place_label=1, trusted_times=trusted_times, verbose=verbose)
        return self.to_df(data, PLACES_HOME_COLUMNS)

    def places_home_friend_df(self, userid, trusted_times=True, verbose=False):
        data = self.places_label(userid, place_label=2, trusted_times=trusted_times, verbose=verbose)
        return self.to_df(data, PLACES_HOME_COLUMNS)

    def places_work_df(self, userid, trusted_times=True, verbose=False):
        data = self.places_label(userid, place_label=3, trusted_times=trusted_times, verbose=verbose)
        return self.to_df(data, PLACES_WORK_COLUMNS)

    def users_list(self, drop_test_users=True):
        result = self.users(drop_test_users=drop_test_users)
        return [user[0] for user in result]

    def to_df(self, data, columns):
        data = pd.DataFrame(data)
        if len(data) > 0:
            data.columns = columns

        return data

    def users_with_places(self, verbose=False, drop_test_users=True):
        query = "SELECT DISTINCT visits_20min.userid FROM visits_20min " + \
        "INNER JOIN places WHERE visits_20min.userid=places.userid;"

        result_users = pd.Series([userid[0] for userid in list(self.sql_query(query, verbose=verbose))])

        if drop_test_users:
            result_users = result_users[result_users.isin(DBDAO().users_df(drop_test_users=True)["userid"])]

        return result_users



    def records_join(self, join_to_table, right_cols=None, how="INNER", record_cols=RECORDS_COLUMNS, userids=None, verbose=False):
        query = "SELECT <columns> FROM records " + how + " JOIN " + join_to_table + " ON records.db_key=" + join_to_table + ".db_key;"

        if right_cols:
            query_records_cols = ["records." + record_col for record_col in record_cols]
            query_right_cols = [join_to_table + "." + right_col for right_col in right_cols]
            columns = ", ".join(query_right_cols + query_records_cols)
        else:
            columns = "*"

        query = query.replace("<columns>", columns)

        if userids:
            query = self.selection_match(query=query, attribute="userid", values=userids, logical_conjunction="OR")

        return self.sql_query(query, verbose=verbose)


    def records(self, userids=None, record_type=None, select_columns="*", verbose=False):
        query = "SELECT %s FROM records;" % (select_columns)

        if userids:
            query = self.selection_match(query=query,
                                         attribute="userid",
                                         values=userids,
                                         logical_conjunction="OR")

        if record_type:
            query = self.selection_match(query=query,
                                         attribute="type",
                                         values=[record_type])

        return self.sql_query(query, verbose=verbose)

    def users(self, drop_test_users=True, userids=None, select_columns="*", verbose=False):
        query = "SELECT %s FROM users;" % (select_columns)

        if userids:
            query = self.selection_match(query=query,
                                         attribute="userid",
                                         values=userids,
                                         logical_conjunction="OR")

        if drop_test_users:
            query = query.replace(";", " WHERE test_user='f'")

        return self.sql_query(query, verbose= verbose)

    def places(self, userids=None, select_columns="*", verbose=False):
        query = "SELECT %s FROM places;" % (select_columns)

        if userids:
            query = self.selection_match(query=query,
                                         attribute="userid",
                                         values=userids,
                                         logical_conjunction="OR")

        return self.sql_query(query, verbose=verbose)

    def gps(self, dbkeys=None, select_columns="*", verbose=False):
        query = "SELECT %s FROM gps;" % (select_columns)

        if dbkeys:
            query = self.selection_match(query, "dbkey", dbkeys, "OR")

        return self.sql_query(query, verbose=verbose)

    def places_label(self, userid, place_label, trusted_times=True, verbose=False):
        query = "SELECT places.userid, places.place_label, places.placeid, visits_20min.time_start, visits_20min.time_end, visits_20min.tz_start, visits_20min.tz_end, visits_20min.trusted_start, visits_20min.trusted_end, visits_20min.trusted_transition " + \
        "FROM places " + \
        "INNER JOIN visits_20min ON places.userid=visits_20min.userid AND places.placeid=visits_20min.placeid " + \
        "WHERE places.place_label={};".format(place_label)

        query = self.selection_match(query, "places.userid", [userid], "AND")

        if trusted_times:
            query = self.selection_match(query, "trusted_start", "t", "AND")
            query = self.selection_match(query, "trusted_end", "t", "AND")
            query = self.selection_match(query, "trusted_transition", "t", "AND")

        return self.sql_query(query, verbose=verbose)

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

    def selection_match(self, query, attribute, values, logical_conjunction=""):

        if "WHERE" in query:
            appendix = " AND "
        else:
            appendix = " WHERE "

        for value in values:
            appendix = appendix + attribute + "=\"" + str(value) + "\" " + logical_conjunction + " "

        appendix = appendix[0:len(appendix) - len(logical_conjunction + " ")]

        return query.replace(";", "") + appendix + ";"


    def close_connection(self):
        self.cnx.close()

    def __del__(self):
        self.close_connection()

