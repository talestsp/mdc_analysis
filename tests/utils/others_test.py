import unittest
from src.utils.others import partition_dict_by_keys_one_vs_all


class others_test(unittest.TestCase):

    def setUp(self):
        pass

    def test_partition_dict_by_keys_one_vs_all(self):
        d = {"user_a": 1,
             "user_b": 2,
             "user_c": 3}

        user_data, rest_data = partition_dict_by_keys_one_vs_all(d, "user_b")

        self.assertEquals(set(rest_data.keys()), set(["user_a", "user_c"]))
        self.assertEquals(user_data, 2)

