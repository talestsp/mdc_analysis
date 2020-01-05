import unittest
import pandas as pd
from src.dao import csv_dao, objects_dao
from src.data_processment.trajectory_cutting import gaps_params, cut_traj_in_trips
from src.taxonomy.category_mapping import users_tags_to_categ


class trajectory_cutting_test(unittest.TestCase):

    def setUp(self):
        self.user_id = "5936"

        self.user_srg = objects_dao.load_stop_region_group_object(self.user_id)
        self.user_gps_data = csv_dao.load_user_gps_csv(self.user_id)
        self.gaps = gaps_params(self.user_gps_data, gap_tresh_minutes=60 * 12)

        pd.set_option('display.float_format', lambda x: '%.3f' % x)

    def test_gaps_params(self):
        self.assertEqual(self.gaps.iloc[0]["start"], 1253806201)
        self.assertEqual(self.gaps.iloc[13]["start"], 1255100576)

    def test_cut_traj_in_trips(self):
        trips = cut_traj_in_trips(srg_sequence_report=self.user_srg.sequence_report(enrich_columns=True), gaps=self.gaps)

        categ_0 = users_tags_to_categ({self.user_id: [sr['tags'] for sr in trips[0]]}, version="0.0.categ_v1", verbose=False)[1]
        categ_1 = users_tags_to_categ({self.user_id: [sr['tags'] for sr in trips[1]]}, version="0.0.categ_v1", verbose=False)[1]
        categ_2 = users_tags_to_categ({self.user_id: [sr['tags'] for sr in trips[2]]}, version="0.0.categ_v1", verbose=False)[1]
        categ_3 = users_tags_to_categ({self.user_id: [sr['tags'] for sr in trips[3]]}, version="0.0.categ_v1", verbose=False)[1]

        self.assertEqual(categ_0[self.user_id], ["liquor_store", "liquor_store", "WORK"])
        self.assertEqual(categ_1[self.user_id], ["political", "lodging"])
        self.assertEqual(categ_2[self.user_id], ["HOME", "WORK", "NoCategoryMatched", "WORK", "store", "WORK"])
        self.assertEqual(categ_3[self.user_id], ["lodging", "travel_agency"])



