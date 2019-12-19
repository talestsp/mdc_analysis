import unittest
import pandas as pd
from src.dao import csv_dao, objects_dao
from src.data_processment.trajectory_cutting import gaps_params, cut_traj_in_trips
from src.taxonomy.category_mapping import tags_to_categ
from datetime import datetime


class trajectory_cutting_test(unittest.TestCase):

    def setUp(self):
        self.user_id = "5936"

        self.user_srg = objects_dao.load_stop_region_group_object(self.user_id)
        self.user_gps_data = csv_dao.load_user_gps_csv(self.user_id)
        self.gaps = gaps_params(self.user_gps_data, 30)

        pd.set_option('display.float_format', lambda x: '%.3f' % x)

    def test_gaps_params(self):
        gaps = gaps_params(self.user_gps_data, gap_tresh_minutes=60 * 12)

        print()
        print(gaps)
        self.assertEqual(gaps.iloc[0]["start"], 1253806201)
        self.assertEqual(gaps.iloc[13]["start"], 1255100576)

    def test_cut_traj_in_trips(self):
        print(self.user_srg.sequence_report(enrich_columns=True).head(12)[["sr", "tags", "start_date", "start_time", "end_date", "end_time"]])

        trips = cut_traj_in_trips(srg_sequence_report=self.user_srg.sequence_report(enrich_columns=True), gaps=self.gaps)

        now = datetime.now()
        categ_0 = tags_to_categ({self.user_id: trips[0]}, version="0.0.categ_v1", verbose=False)[1]
        print(datetime.now() - now)
        now = datetime.now()
        categ_1 = tags_to_categ({self.user_id: trips[1]}, version="0.0.categ_v1", verbose=False)[1]
        print(datetime.now() - now)
        now = datetime.now()
        categ_2 = tags_to_categ({self.user_id: trips[2]}, version="0.0.categ_v1", verbose=False)[1]
        print(datetime.now() - now)
        now = datetime.now()
        categ_3 = tags_to_categ({self.user_id: trips[3]}, version="0.0.categ_v1", verbose=False)[1]
        print(datetime.now() - now)
        now = datetime.now()

        print(trips[0])
        print(categ_0["5936"])
        print()
        print(trips[1])
        print(categ_1["5936"])
        print()
        print(trips[2])
        print(categ_2["5936"])
        print()
        print(trips[3])
        print(categ_3["5936"])

        self.assertEqual(categ_0[self.user_id], ["liquor_store", "WORK"])
        self.assertEqual(categ_1[self.user_id], ["political", "lodging"])
        self.assertEqual(categ_2[self.user_id], ["HOME", "WORK", "NoCategoryMatched", "WORK", "store", "WORK"])
        self.assertEqual(categ_3[self.user_id], ["lodging", "travel_agency"])



