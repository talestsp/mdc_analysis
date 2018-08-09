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

    sr = MovingCentroidStopRegionFinder(d, delta_t)

    start_time = time.time()
    for i in range(len(user_data)):
        print(i, "out of", len(user_data))

        point = user_data.iloc[i]
        sr.online_location_point_checking(point)
        if sr.is_stop_region():
            clusters.append(sr.get_last_stop_region_detected())
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

    return clusters


class StopRegionsFinder:

    def __init__(self, region_radius, delta_time):
        self.region_radius = region_radius
        self.delta_time = delta_time

        self.cluster = pd.DataFrame()
        self.centroid = None

        self.last_cluster = pd.DataFrame()
        self.last_cluster_centroid = None

    def online_location_point_checking(self, point):
        raise NotImplementedError

    def cluster_centroid(self, cluster):
        length = len(cluster)
        sum_lat = cluster["latitude"].sum()
        sum_lon = cluster["longitude"].sum()
        points_centroid = {"latitude": sum_lat / length, "longitude": sum_lon / length}
        return points_centroid

    def distance(self, point_a, point_b):
        return self.__haversine_vectorized(point_a["longitude"], point_a["latitude"], point_b["longitude"],
                                           point_b["latitude"])

    def __haversine_vectorized(self, lon1, lat1, lon2, lat2):
        """
        Calculate the great circle distance in meters between two points
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
            counter += 1
            if verbose:
                print(counter, "out of", len_location_df)
            point = location_row[1]

            self.online_location_point_checking(point)

            if self.is_stop_region(is_last_point=counter==len_location_df - 1):
                clusters.append(self.get_last_stop_region_detected(counter==len_location_df))
                if verbose:
                    print("CLUSTERRRRRRR")
                    print(clusters[-1])
        return clusters


    def is_stop_region(self, is_last_point=False):
        if is_last_point:
            return self.cluster_delta_time(self.last_cluster) >= self.delta_time
        else:
            return len(self.last_cluster) > 1 and len(self.last_cluster) > len(self.cluster) and self.cluster_delta_time(self.last_cluster) >= self.delta_time

    def get_last_stop_region_detected(self, is_last_point=False):
        if self.is_stop_region() and is_last_point:
            return self.cluster
        elif self.is_stop_region() and not is_last_point:
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

    stop_regions(data)


