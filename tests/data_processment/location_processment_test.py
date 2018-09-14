import unittest
import pandas as pd
from src.data_processment.stop_region import MovingCentroidStopRegionFinder


class location_processment_test(unittest.TestCase):

    def setUp(self):
        pass

    def test_optimum_cluster(self):
        data = pd.read_csv("tests/data/optimum_cluster.csv")
        sr = MovingCentroidStopRegionFinder(region_radius=1255976, delta_time=60)

        clusters = []

        for row in data.iterrows():
            point = row[1]
            sr.online_location_point_checking(point)

            if sr.is_stop_region():
                clusters.append(sr.get_last_stop_region_detected())

        self.assertEqual(1, len(clusters))

    def test_cluster_centroid(self):
        data = pd.read_csv("tests/data/cluster_centroid.csv")
        sr = MovingCentroidStopRegionFinder(region_radius=1255976, delta_time=60)

        for row in data.iterrows():
            point = row[1]
            sr.online_location_point_checking(point)
            c = sr.cluster_centroid(sr.cluster)

        c = sr.cluster_centroid(sr.cluster)
        self.assertEqual(5.5, c["latitude"])
        self.assertEqual(2, c["longitude"])

    def test_distance(self):
        sr = MovingCentroidStopRegionFinder(region_radius=100000000000, delta_time=60)

        d = sr.distance({"latitude": -7.2376725, "longitude": -35.8830033},
                        {"latitude": -7.2372265, "longitude": -35.8781688})
        self.assertAlmostEqual(535.91, d, delta=50)


        d = sr.distance({"latitude": -7.2376725, "longitude": -35.8830033},
                        {"latitude": -7.2133644, "longitude": -35.9075357})
        self.assertAlmostEqual(3830, d, delta=50)

    def test_detect_clusters(self):
        data = pd.read_csv("tests/data/clusters.csv")
        sr = MovingCentroidStopRegionFinder(region_radius=1255976, delta_time=60)

        clusters = sr.find_clusters(data)
        self.assertEqual(2, len(clusters))


    def test_detect_clusters_2(self):
        data = pd.read_csv("tests/data/clusters2.csv")
        sr = MovingCentroidStopRegionFinder(region_radius=1255976, delta_time=60)

        clusters = sr.find_clusters(data)
        self.assertEqual(2, len(clusters))
