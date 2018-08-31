from src.plot.stop_region_plot import plot_stop_region, plot_user_loc
from src.utils.geo import cluster_centroid

class AnimatedPlot:

    def __init__(self, user_data, clusters, title):
        self.user_data = user_data
        self.title = title
        self.next_point_i = 0

        self.indexed_clusters = {}

        if clusters:
            for cluster in clusters:
                cluster = cluster.sort_values(by="time")
                self.indexed_clusters[int(cluster.tail(1)["time"])] = cluster


    def build_base_plot(self, color="navy", alpha=0.2):
        return plot_user_loc(self.user_data, self.title, color=color, alpha=alpha)

    def build_stop_region_plot(self, color="navy", circle_alpha=0.2, cluster_alpha=0.2):
        return plot_stop_region(self.user_data, [self.indexed_clusters[key] for key in self.indexed_clusters.keys()],
                                self.title, color=color, circle_alpha=circle_alpha, cluster_alpha=cluster_alpha)

    def get_next_point(self, reset=False):
        if reset:
            self.next_point_i = 0

        next_point = self.user_data.iloc[self.next_point_i]
        self.next_point_i += 1

        for cluster_timestamp in self.indexed_clusters.keys():
            if next_point["time"] >= cluster_timestamp:
                cluster_found = self.indexed_clusters[cluster_timestamp]
                del self.indexed_clusters[cluster_timestamp]

                return {"point": next_point, "centroid": cluster_centroid(cluster_found)}

        return {"point": next_point, "centroid": None}