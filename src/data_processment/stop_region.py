import time
import pandas as pd
import numpy as np
from src.utils.geo import haversine_vectorized, cluster_centroid
#from src.dao.dbdao import DBDAO

class StopRegionsFinder:

    def __init__(self, region_radius, delta_time):
        '''
        Finds the places that the user has stopped within a time interval and a circumference.
        :param user_data: user data with latitude, longitude and time.
        :param region_radius: redius (in meters) of the tolerate location circumference delimiting its region
        :param delta_time: minimum time (in seconds) to consider the point as as stop region
        '''
        self.region_radius = region_radius
        self.delta_time = delta_time

        self.cluster = pd.DataFrame()
        self.centroid = None

        self.last_cluster = pd.DataFrame()
        self.last_cluster_centroid = None

    def online_location_point_checking(self, point):
        raise NotImplementedError

    def cluster_centroid(self, cluster):
        return cluster_centroid(cluster)

    def distance(self, point_a, point_b):
        return haversine_vectorized(point_a["longitude"], point_a["latitude"], point_b["longitude"],
                                           point_b["latitude"])

    def cluster_delta_time(self, cluster):
        return cluster["time"].iloc[len(cluster) - 1] - cluster["time"].iloc[0]


class MovingCentroidStopRegionFinder(StopRegionsFinder):

    def online_location_point_checking(self, point):
        self.last_cluster = self.cluster
        self.last_cluster_centroid = self.centroid

        if len(self.cluster) > 0 and self.distance(point, self.centroid) > 1.5 * self.region_radius:
            self.cluster = pd.DataFrame()
            self.cluster = self.cluster.append(point)
            self.centroid = self.cluster_centroid(self.cluster)

        else:
            self.cluster = self.cluster.append(point)
            self.centroid = self.cluster_centroid(self.cluster)
            self.__remove_outer_points()

    def find_clusters(self, location_df, verbose=False):
        clusters = []
        counter = 0
        len_location_df = len(location_df)
        location_df = location_df.drop_duplicates().sort_values(by="time")

        for location_row in location_df.iterrows():
            if verbose:
                print(counter, "out of", len_location_df)

            point = location_row[1]

            self.online_location_point_checking(point)

            is_last_point = counter == len_location_df - 1
            if self.is_stop_region(is_last_point):
                cluster = self.get_last_stop_region_detected(is_last_point)
                clusters.append(cluster)
                if verbose:
                    print("CLUSTERRRRRRR")
                    print(clusters[-1])
            counter += 1
        return clusters


    def is_stop_region(self, is_last_point=False):
        if is_last_point:
            return self.cluster_delta_time(self.last_cluster) >= self.delta_time
        else:
            return len(self.last_cluster) > 1 and len(self.last_cluster) > len(self.cluster) and self.cluster_delta_time(self.last_cluster) >= self.delta_time

    def get_last_stop_region_detected(self, is_last_point=False):
        if self.is_stop_region(is_last_point) and is_last_point:
            return self.cluster
        elif self.is_stop_region(is_last_point) and not is_last_point:
            return self.last_cluster
        else:
            return None

    def __remove_outer_points(self):
        for row in self.cluster.iterrows():
            point = row[1]
            distance = self.distance(self.centroid, point)
            if distance > self.region_radius:
                #TO THINK - prunning not necessary then it stays robust against outlier points duye to measurement errors
                self.cluster = self.cluster.drop(point.name)

    def size(self):
        return len(self.cluster)



class StopRegionEvaluator:

    def __init__(self):
        pass




if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    pd.set_option('display.float_format', lambda x: '%.3f' % x)

    data = pd.read_csv("outputs/user_gps/6171_gps.csv").drop_duplicates().sort_values(by="time")[0:267]



