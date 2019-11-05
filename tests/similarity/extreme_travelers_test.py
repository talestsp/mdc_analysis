import unittest

from src.dao import csv_dao
from src.dao import objects_dao
from src.similarity.extreme_travelers import sequence_report, first_trip_of_the_day, last_trip_of_the_day

import pandas as pd
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

class extreme_travelers_test(unittest.TestCase):

    def setUp(self):
        user_id = 5928
        self.srg = objects_dao.load_stop_region_group_object(user_id)

    def test_first_trip_of_the_day(self):
        rep = sequence_report(self.srg)
        first_trips = first_trip_of_the_day(rep)

        sr_ids = ["5928_1", "5928_3", "agg_5928_4", "agg_5928_8", "agg_5928_13", "agg_5928_38", "5928_40"]

        for i in range(len(sr_ids)):
            self.assertEquals(first_trips.index.tolist()[i], sr_ids[i])

    def test_last_trip_of_the_day(self):
        rep = sequence_report(self.srg)
        rep["day"] = rep["start_date"].apply(lambda value : value.split("-")[2])
        last_trips = last_trip_of_the_day(rep)

        sr_ids = ["5928_2", "agg_5928_4", "agg_5928_8", "agg_5928_10", "agg_5928_18", "agg_5928_38", "5928_41"]

        for i in range(len(sr_ids)):
            self.assertEquals(last_trips.index.tolist()[i], sr_ids[i])
