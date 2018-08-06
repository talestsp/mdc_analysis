import math
import pandas as pd
from src.dao.dbdao import DBDAO

def stop_regions(user_data, d=1, delta_t=300):
    '''
    Returns the places that the user has stopped within a time interval and a circumference.
    :param user_data: user data with latitude, longitude and time.
    :param d: redius (in meters) of the tolerate location circumference delimiting its region
    :param delta_t: minimum time (in seconds) to consider the point as as stop region
    :return: a list of centroids representing the user stops
    '''

    user_data = user_data.sort_values(by="time")
    print(user_data.head())

    sr = StopRegion(d, delta_t)

    for i in range(len(user_data)):
        point = user_data.iloc[i]
        print("\n\n\n\n====================================================")
        print("----\n")
        sr.check_location_point(point)
        if len(sr.cluster) > 2:
            print("CLUSTER::::")
            print(sr.cluster)


class StopRegion:

    def __init__(self, radius_m, delta_time):
        self.radius = radius_m * (0.00001 / 1.1132)
        self.delta_time = delta_time

        self.cluster = pd.DataFrame()
        self.centroid = None

        self.last_cluster = pd.DataFrame()
        self.last_cluster_centroid = None

    def cluster_centroid(self):
        length = len(self.cluster)
        sum_lat = self.cluster["latitude"].sum()
        sum_lon = self.cluster["longitude"].sum()
        points_centroid = {"latitude": sum_lat / length, "longitude": sum_lon / length}
        return points_centroid

    def euclidean_distance(self, point_a, point_b):
        return math.sqrt((point_a["longitude"] - point_b["longitude"]) ** 2 + (point_a["latitude"] - point_b["latitude"]) ** 2)

    def check_location_point(self, point):
        print("CHECKING POINT:")
        print(point)

        self.last_cluster = self.cluster
        self.last_cluster_centroid = self.centroid

        self.cluster = self.cluster.append(point)
        self.centroid = self.cluster_centroid()

        self.__remove_outer_points()

    def is_stop_region(self):
        # due to points removing from cluster each time a point is checked there is no need to check the radius again
        return self.cluster_delta_time() >= self.delta_time

    def get_stop_region_cluster(self):
        if self.is_stop_region():
            return self.__get_optimum_cluster()
        else:
            return None

    def __check_optimum_location(self):
        return len(self.last_cluster) > len(self.cluster)

    def __get_optimum_cluster(self):
        if self.__check_optimum_location():
            return self.last_cluster
        else:
            return self.cluster

    def cluster_delta_time(self):
        return self.cluster["time"][-1] - self.cluster["time"][1]

    def points_delta_time(self, point_a, point_b):
        return abs(point_b["time"] - point_a["time"])

    def __remove_outer_points(self):
        for row in self.cluster.iterrows():
            point = row[1]
            if self.euclidean_distance(self.centroid, point) > self.radius:
                print()
                print(">>> REMOVING POINT:")
                print(point)
                # print(self.euclidean_distance(self.centroid, point), self.radius)
                # print(float(self.euclidean_distance(self.centroid, point)))
                #TO THINK - prunning not necessary then it stays robust against outlier points duye to measurement errors
                self.cluster = self.cluster.drop(point.name)

    def size(self):
        return len(self.cluster)



if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    pd.set_option('display.float_format', lambda x: '%.3f' % x)

    data = pd.read_csv("outputs/user_gps/6187_gps.csv")
    stop_regions(data)


