import time
import pandas as pd
import numpy as np
#from src.dao.dbdao import DBDAO

def stop_regions(user_data, d=50, delta_t=60):
    '''
    Returns the places that the user has stopped within a time interval and a circumference.
    :param user_data: user data with latitude, longitude and time.
    :param d: redius (in meters) of the tolerate location circumference delimiting its region
    :param delta_t: minimum time (in seconds) to consider the point as as stop region
    :return: a list of centroids representing the user stops
    '''

    user_data = user_data.sort_values(by="time")
    print(user_data.head())

    clusters = []

    sr = StopRegion(d, delta_t)

    start_time = time.time()
    for i in range(len(user_data)):
        print(i, "out of", len(user_data))

        point = user_data.iloc[i]
        sr.check_location_point(point)
        if sr.is_optimum_cluster():
            clusters.append(sr.get_optimum_cluster())
            print("CLUSTERRRRRRR")
            print(clusters[-1])

    print(time.time() - start_time)
    counter = 0
    for cluster in clusters:
        counter += 1
        cluster.to_csv("clusters_temp/cluster_" + str(counter) + ".csv", index=False)

        print(cluster)
        print(sr.cluster_centroid(cluster))
        print("-----------------------------\n\n")


class StopRegion:

    def __init__(self, region_radius, delta_time):
        self.region_radius = region_radius
        self.delta_time = delta_time

        self.cluster = pd.DataFrame()
        self.centroid = None

        self.last_cluster = pd.DataFrame()
        self.last_cluster_centroid = None

    def check_location_point(self, point):
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

        print(point["latitude"], point["longitude"])
        print("cluster size:", len(self.cluster))
        print("centroid:", self.centroid)
        print("delta t:", self.cluster_delta_time(self.cluster))
        print()

    def cluster_centroid(self, cluster):
        length = len(cluster)
        sum_lat = cluster["latitude"].sum()
        sum_lon = cluster["longitude"].sum()
        points_centroid = {"latitude": sum_lat / length, "longitude": sum_lon / length}
        return points_centroid

    def distance(self, point_a, point_b):
        return self.__haversine_vectorized(point_a["longitude"], point_a["latitude"], point_b["longitude"], point_b["latitude"])

    def __haversine_vectorized(self, lon1, lat1, lon2, lat2):
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)
        Adapted from code found at: https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
        """
        # Convert decimal degrees to Radians:
        lon1 = np.radians(lon1)
        lat1 = np.radians(lat1)
        lon2 = np.radians(lon2)
        lat2 = np.radians(lat2)
        # Implementing Haversine Formula:
        dlon = np.subtract(lon2, lon1)
        dlat = np.subtract(lat2, lat1)
        a = np.add(np.power(np.sin(np.divide(dlat, 2)), 2),
                   np.multiply(np.cos(lat1),
                               np.multiply(np.cos(lat2),
                                           np.power(np.sin(np.divide(dlon, 2)), 2))))
        c = np.multiply(2, np.arcsin(np.sqrt(a)))
        r = 6371
        return c * r * 1000

    def is_optimum_cluster(self):
        return len(self.last_cluster) > 1 and len(self.last_cluster) > len(self.cluster) and self.cluster_delta_time(self.last_cluster) >= self.delta_time

    def get_optimum_cluster(self):
        if self.is_optimum_cluster():
            return self.last_cluster
        else:
            return self.cluster

    def is_stop_region(self):
        # due to points removing from cluster each time a point is checked there is no need to check the radius again
        return len(self.cluster) > 1 and self.cluster_delta_time(self.cluster) >= self.delta_time

    def cluster_delta_time(self, cluster):
        return cluster["time"].iloc[len(cluster) - 1] - cluster["time"].iloc[0]

    def __remove_outer_points(self):
        for row in self.cluster.iterrows():
            point = row[1]
            distance = self.distance(self.centroid, point)
            if distance > self.region_radius:
                #TO THINK - prunning not necessary then it stays robust against outlier points duye to measurement errors
                self.cluster = self.cluster.drop(point.name)

    def size(self):
        return len(self.cluster)



if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    pd.set_option('display.float_format', lambda x: '%.3f' % x)

    data = pd.read_csv("outputs/user_gps/6171_gps.csv").drop_duplicates().sort_values(by="time")[0:267]

    stop_regions(data)


