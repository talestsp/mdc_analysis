import unittest
from src.data_processment.input_data_version import InputDataManager


class input_data_version_test(unittest.TestCase):

    def setUp(self):
        self.data_manager = InputDataManager()

    def test_version_raw_tags_0_0(self):
        input_data = self.data_manager.get_input_data("raw_tags-0.0")

        tags = [["liquor_store", "food", "store"],
                ["bus_station", "transit_station"],
                ["HOME"],
                ["museum", "insurance_agency", "finance", "finance"],
                ["parking"],
                ["airport"]]

        self.assertEquals(input_data["user_data"]["6015"][0:6], tags)

        tags = [["health"],
                ["restaurant", "food"],
                ["restaurant", "food"],
                ["HOME"],
                ["restaurant", "food"]]

        self.assertEquals(input_data["user_data"]["6015"][166:171], tags)

    def test_version_raw_tags_0_1(self):
        input_data = self.data_manager.get_input_data("raw_tags-0.1")

        tags = [["health"],
                ["restaurant", "food"],
                ["HOME"],
                ["restaurant", "food"],
                ["pharmacy", "health", "store"]]

        self.assertEquals(input_data["user_data"]["6015"][162:167], tags)

    def test_0_0_categ_v1(self):
        raw_tags = self.data_manager.get_input_data("raw_tags-0.0")["user_data"]["6015"]

        categs_multi_trip = self.data_manager.users_multi_trip(gap_tresh_minutes=60 * 12,
                                                               sr_stay_time_minutes=5,
                                                               version="0.0.categ_v1")["6015"]

        soma_categs_multi_trip = 0
        for trip in categs_multi_trip:
            soma_categs_multi_trip += len(trip)

        print('''categs_multi_trip''')
        print(categs_multi_trip)

        print("\n\n\n")

        print('''raw_tags''')
        print(raw_tags)

        print("\n\n\n")

        print("len(raw_tags):", len(raw_tags))
        print("soma_categs_multi_trip:", soma_categs_multi_trip)

        # self.assertEqual(len(raw_tags), soma_categs_multi_trip)

    def test_0_1_categ_v1(self):
        raw_tags = self.data_manager.get_input_data("raw_tags-0.1")["user_data"]["6015"]

        categs_multi_trip = self.data_manager.users_multi_trip(gap_tresh_minutes=60 * 12,
                                                    sr_stay_time_minutes=5,
                                                    version="0.1.categ_v1")["6015"]

        soma_categs_multi_trip = 0
        for trip in categs_multi_trip:
            soma_categs_multi_trip += len(trip)

        self.assertEqual(len(raw_tags), soma_categs_multi_trip)
