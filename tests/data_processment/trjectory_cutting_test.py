import unittest
import pandas as pd
from src.dao import csv_dao, objects_dao
from src.data_processment.trajectory_cutting import gaps_params, cut_traj_in_trips


class trajectory_cutting_test(unittest.TestCase):

    def setUp(self):
        user_id = "6189"

        self.user_srg = objects_dao.load_stop_region_group_object(user_id)
        self.user_gps_data = csv_dao.load_user_gps_csv(user_id)
        self.gaps = gaps_params(self.user_gps_data, 30)



    def test_cut_traj_in_trips(self):

        cut_traj_in_trips(srg_sequence_report=self.user_srg.sequence_report(), gaps=self.gaps)