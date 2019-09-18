import unittest
from src.poi_grabber import google_places


class csv_dao_test(unittest.TestCase):

    def setUp(self):
        self.google_pois = google_places.load_all_google_places_data(valid_pois=True)

    def test_load_valids(self):
        for types in self.google_pois["types"]:
            if len(types) == 2:
                self.assertNotEquals(set(["point_of_interest", "establishment"]), set(types))

            if len(types) == 3:
                self.assertNotEquals(set(["point_of_interest", "establishment", "premise"]), set(types))