import pandas as pd
import numpy as np

class StopRegionsFinder:

    def __init__(self, region_radius, delta_time, consecutive_outliers_tolerance=1):
        '''
        Finds the places that the user has stopped within a time interval and a circumference.
        :param user_data: user data with latitude, longitude and time.
        :param region_radius: redius (in meters) of the tolerate location circumference delimiting its region
        :param delta_time: minimum time (in seconds) to consider the point as as stop region
        '''
        self.region_radius = region_radius
        self.delta_time = delta_time
        self.consecutive_outliers_tolerance = consecutive_outliers_tolerance
        self.consecutive_outliers_counter = 0

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
        if len(cluster) == 0:
            return -1

        if len(cluster) == 1:
            return 0

        return cluster["local_time"].iloc[len(cluster) - 1] - cluster["local_time"].iloc[0]


class MovingCentroidStopRegionFinder(StopRegionsFinder):


    def online_location_point_checking(self, point):
        self.last_cluster = self.cluster
        self.last_cluster_centroid = self.centroid

        if (not self.reached_maximum_cluster_size()) and (len(self.cluster) == 0 or self.check_outlier_tolerance(point, self.last_cluster)):
            self.cluster = self.cluster.append(point)
            self.centroid = self.cluster_centroid(self.cluster)
            self.__remove_outer_points()

        else:
            self.cluster = pd.DataFrame()
            self.cluster = self.cluster.append(point)
            self.centroid = self.cluster_centroid(self.cluster)

    def find_clusters(self, location_df, n_limit_clusters=None, verbose=False):
        clusters = []
        counter = 0
        len_location_df = len(location_df)
        #print(location_df)
        location_df = location_df.drop_duplicates().sort_values(by="local_time")

        for location_row in location_df.iterrows():
            if not n_limit_clusters is None and len(clusters) > n_limit_clusters:
                break
                
            if verbose:
                print(counter, "out of", len_location_df)
                print("n clusters:", len(clusters), ", ", "current cluster size:", len(self.last_cluster))

            point = location_row[1]

            self.online_location_point_checking(point)

            is_last_point = counter == len_location_df - 1
            if self.is_stop_region(is_last_point):
                cluster = self.get_last_stop_region_detected(is_last_point)[['local_time', 'latitude', 'longitude', 'horizontal_accuracy', 'speed_accuracy', 'time', 'speed', 'tz', 'userid']]
                clusters.append(cluster)
                if verbose:
                    print("CLUSTERRRRRRR")
                    print(clusters[-1])
            counter += 1
        return clusters

    def check_outlier_tolerance(self, point, cluster):
        """
        Returns True if the number of consecutive outlier points if less than the consecutive outliers threshold.
        Outlier point is a point that its distance to the centroid is greater than the region_radius.
        :param point:
        :param cluster:
        :return:
        """
        centroid = cluster_centroid(cluster)

        if haversine_vectorized(lat1=point["latitude"], lon1=point["longitude"], lat2=centroid["latitude"], lon2=centroid["longitude"]) > self.region_radius:
            self.consecutive_outliers_counter += 1
        else:
            self.consecutive_outliers_counter = 0

        return self.consecutive_outliers_counter <= self.consecutive_outliers_tolerance

    def is_stop_region(self, is_last_point=False):
        if is_last_point:
            return self.cluster_delta_time(self.last_cluster) >= self.delta_time

        elif len(self.last_cluster) > 0 and len(self.last_cluster) > len(self.cluster) and self.cluster_delta_time(self.last_cluster) >= self.delta_time:
            return True

        elif len(self.last_cluster) > 0 and len(self.last_cluster) +1 == len(self.cluster) and self.reached_maximum_cluster_size():
            return True

        else:
            return False

    def reached_maximum_cluster_size(self):
        if len(self.last_cluster) <= 1:
            return False
        return self.cluster_delta_time(self.last_cluster) >= 5 * self.delta_time

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
                self.cluster = self.cluster.drop(point.name)

    def size(self):
        return len(self.cluster)



def haversine_vectorized(lon1, lat1, lon2, lat2):
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

def cluster_centroid(cluster):
    count = cluster["latitude"].count() # count() instead of len() to avoid count nan values
    sum_lat = cluster["latitude"].sum()
    sum_lon = cluster["longitude"].sum()
    points_centroid = {"latitude": sum_lat / count, "longitude": sum_lon / count}
    return points_centroid



