import unittest
import pandas as pd
from src.data_processment.location_processment import StopRegion


class location_processment_test(unittest.TestCase):

    def setUp(self):
        pass

    def test_optimum_cluster(self):
        data = pd.read_csv("src/tests/data/optimum_cluster.csv")
        sr = StopRegion(region_radius=1255976, delta_time=60)

        clusters = []

        for row in data.iterrows():
            point = row[1]
            sr.check_location_point(point)

            if sr.is_optimum_cluster():
                clusters.append(sr.get_optimum_cluster())

        self.assertEqual(1, len(clusters))

    def test_cluster_centroid(self):
        data = pd.read_csv("src/tests/data/cluster_centroid.csv")
        sr = StopRegion(region_radius=1255976, delta_time=60)

        for row in data.iterrows():
            point = row[1]
            sr.check_location_point(point)
            c = sr.cluster_centroid(sr.cluster)

        c = sr.cluster_centroid(sr.cluster)
        self.assertEqual(5.5, c["latitude"])
        self.assertEqual(2, c["longitude"])

    def test_distance(self):
        sr = StopRegion(region_radius=100000000000, delta_time=60)

        d = sr.distance({"latitude": -7.2376725, "longitude": -35.8830033},
                        {"latitude": -7.2372265, "longitude": -35.8781688})
        self.assertAlmostEqual(535.91, d, delta=50)


        d = sr.distance({"latitude": -7.2376725, "longitude": -35.8830033},
                        {"latitude": -7.2133644, "longitude": -35.9075357})
        self.assertAlmostEqual(3830, d, delta=50)

    def test_detect_clusters(self):
        data = pd.read_csv("src/tests/data/clusters.csv")
        sr = StopRegion(region_radius=1255976, delta_time=60)

        clusters = []

        for row in data.iterrows():
            point = row[1]
            sr.check_location_point(point)
            if sr.is_optimum_cluster():
                clusters.append(sr.get_optimum_cluster())

        print("*****************************************************")
        print("*****************************************************")
        for cluster in clusters:
            print(cluster)
            print("\n\n")

        self.assertEqual(2, len(clusters))


