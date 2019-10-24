import os
os.chdir("/home/tales/dev/master/mdc_analysis/")

import unittest
from src.dao import csv_dao
from src.entity.stop_region import group_stop_regions_for_agglutination, same_closest_poi, same_not_null_semantics
from src.entity.stop_region import StopRegionGroup

class stop_region_agglutination_test(unittest.TestCase):

    def setUp(self):
        pass

    def test_stop_region_agglutination(self):
        sr_sequence = csv_dao.stop_region_sequence(6070)

        # for sr in sr_sequence[199:202]:
        #     print()
        #     print(sr.start_time)
        #     print(sr.end_time)
        #     print(sr.sr_id)
        #     print(sr.semantics)

        agg_sr = sr_sequence[200].agglutinate_with([sr_sequence[199], sr_sequence[201]])

        self.assertEqual(agg_sr.start_time, 1280889770)
        self.assertEqual(agg_sr.end_time, 1280894296)
        self.assertEqual(agg_sr.sr_id, "agg_6070_199")
        self.assertEqual(agg_sr.semantics, [])
        self.assertEqual(agg_sr.user_id, 6070)

    def test_agglutination_choices(self):
        sr_sequence = csv_dao.stop_region_sequence(6070)
        agglutinate, agglut_report = group_stop_regions_for_agglutination(sr_sequence, same_closest_poi, same_closest_poi)

        # print(agglut_report)

        sr_ids = []
        for group in agglutinate:
            if group[0].sr_id == "6070_198":
                for sr in group:
                    sr_ids.append(sr.sr_id)
                break

        self.assertIn("6070_198", sr_ids)
        self.assertIn("6070_199", sr_ids)
        self.assertIn("6070_200", sr_ids)
        self.assertIn("6070_201", sr_ids)
        self.assertIn("6070_202", sr_ids)
        self.assertIn("6070_203", sr_ids)
        self.assertIn("6070_204", sr_ids)
        self.assertIn("6070_205", sr_ids)
        self.assertEqual(8, len(group))

    def test_agglutination_result(self):
        sr_sequence = csv_dao.stop_region_sequence(6070)[198:206]
        sr_agglutinated = sr_sequence[0].agglutinate_with(sr_sequence[4:] + sr_sequence[1:4])

        sr_ids = []

        for sr in sr_agglutinated.agglutination:
            sr_ids.append(sr.sr_id)
            # print(sr.sr_id)

        self.assertIn("6070_198", sr_ids)
        self.assertIn("6070_199", sr_ids)
        self.assertIn("6070_200", sr_ids)
        self.assertIn("6070_201", sr_ids)
        self.assertIn("6070_202", sr_ids)
        self.assertIn("6070_203", sr_ids)
        self.assertIn("6070_204", sr_ids)
        self.assertIn("6070_205", sr_ids)
        self.assertEqual(8, len(sr_agglutinated.agglutination))

        self.assertEqual("agg_6070_198", sr_agglutinated.sr_id)

    def test_agglutination_sequence_result(self):
        sr_list = csv_dao.stop_region_sequence(6070)[195:206]
        group_agglutinated = StopRegionGroup(sr_list[4:] + sr_list[2:4] + sr_list[0:2]).agglutinate_stop_regions()

        sr_ids = []
        sr_ids_inside_agglutination = []

        for sr in group_agglutinated.stop_region_list:
            if sr.is_agglutination():
                for sr_inside in sr.agglutination:
                    sr_ids_inside_agglutination.append(sr_inside.sr_id)
                sr_ids.append(sr.sr_id)

            else:
                sr_ids.append(sr.sr_id)

        self.assertIn("6070_195", sr_ids)
        self.assertIn("agg_6070_196", sr_ids)
        self.assertIn("agg_6070_198", sr_ids)

        self.assertIn("6070_196", sr_ids_inside_agglutination)
        self.assertIn("6070_197", sr_ids_inside_agglutination)
        self.assertIn("6070_198", sr_ids_inside_agglutination)
        self.assertIn("6070_199", sr_ids_inside_agglutination)
        self.assertIn("6070_200", sr_ids_inside_agglutination)
        self.assertIn("6070_201", sr_ids_inside_agglutination)
        self.assertIn("6070_202", sr_ids_inside_agglutination)
        self.assertIn("6070_203", sr_ids_inside_agglutination)
        self.assertIn("6070_204", sr_ids_inside_agglutination)
        self.assertIn("6070_205", sr_ids_inside_agglutination)
        self.assertEqual(3, group_agglutinated.size())

        self.assertEqual(10, len(sr_ids_inside_agglutination))



