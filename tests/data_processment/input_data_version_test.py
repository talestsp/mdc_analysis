import unittest
import pandas as pd
from src.dao import csv_dao
from src.data_processment.input_data_version import InputDataManager


class input_data_version_test(unittest.TestCase):

    def setUp(self):
        self.data_manager = InputDataManager()

    def test_version_markov_0_0(self):
        input_data = self.data_manager.get_input_data("markov-0.0")
        self.assertTrue(len(input_data) > 150)

    def test_0_0_categ_v1(self):
        input_data = self.data_manager.get_input_data("0.0.categ_v1")
        self.assertTrue(len(input_data) > 150)

    def test_0_1_categ_v1(self):
        input_data = self.data_manager.get_input_data("0.1.categ_v1")
        self.assertTrue(len(input_data) > 150)

