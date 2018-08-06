import math
import pandas as pd

def stop_regions(user_data, d, delta_t):
    '''
    Returns the places that the user has stopped within a time interval and a circumference.
    :param user_data: user data with latitude, longitude and time.
    :param d: redius of the tolerate location circumference delimiting its region
    :param delta_t: minimum time to consider the point as as stop region
    :return: a list of centroids representing the user stops
    '''
    points_cluster = []
    points_cluster_centroid = None

    user_data = user_data["time"].sort_values()
    max_time = user_data["time"].iloc[len(user_data) - 1]

    for i in range(len(user_data)):
        point = user_data.iloc[i]

        if len(points_cluster) == 0:
            points_cluster = [point]
            points_cluster_centroid = centroid(points_cluster)

        next_point = user_data.iloc[i + 1]
        if point["time"] < max_time:
            distance = euclidean_distance(points_cluster_centroid, next_point)

            if distance <= d and cluster_delta_time(points_cluster) < delta_t:
                points_cluster.append(next_point)
                points_cluster_centroid = centroid(points_cluster)

            else:
                points_cluster = [] #no valid cluster found, start another cluster




def euclidean_distance(point_a, point_b):
    return math.sqrt( (point_a["longitude"] - point_b["longitude"]) ** 2 + (point_a["latitude"] - point_b["latitude"]) ** 2)

def cluster_delta_time(points_cluster):
    return points_cluster["time"][-1] - points_cluster["time"][1]

def centroid(points_cluster):
    length = len(points_cluster)
    sum_lat = points_cluster["latitude"].sum()
    sum_lon = points_cluster["longitude"].sum()
    return sum_lat/length, sum_lon/length

class StopRegion:

    def __init__(self):
        self.points = pd.DataFrame()
        self.points_centroid = None

    def centroid(self):
        length = len(self.points)
        sum_lat = self.points["latitude"].sum()
        sum_lon = self.points["longitude"].sum()
        self.points_centroid = sum_lat / length, sum_lon / length
        return self.points_centroid

    def delta_time(self):
        return self.points["time"][-1] - self.points["time"][1]

    def add_location(self, point):
        self.points = self.points.append(point)


class MovingWindowRegion:

    def __init__(self):
        self.window_points = []

