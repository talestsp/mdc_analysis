from src.plot.plot import plot_stop_region_with_trajectory, plot_user_loc
from src.utils.geo import cluster_centroid, index_clusters
from src.dao import objects_dao

class AnimatedPlot:

    def __init__(self, user_data, clusters, title):
        self.user_data = user_data
        self.title = title
        self.next_point_i = 0

        self.indexed_clusters = {}

        if clusters:
            self.indexed_clusters = index_clusters(clusters)


    def build_base_plot(self, color="navy", alpha=0.2):
        return plot_user_loc(self.user_data, self.title, color=color, alpha=alpha)

    def build_stop_region_plot(self, color="navy", circle_alpha=0.2, cluster_alpha=0.2):
        return plot_stop_region_with_trajectory(self.user_data, [self.indexed_clusters[key] for key in self.indexed_clusters.keys()],
                                                self.title, color=color, circle_alpha=circle_alpha, cluster_alpha=cluster_alpha)

    def build_stop_region_group_quick_plot(self):
        srg = objects_dao.load_stop_region_group_object(self.user_data["userid"].drop_duplicates().item())
        sub_srg = srg.subsequence(from_ts=self.user_data["local_time"].min(), to_ts=self.user_data["local_time"].max())
        return sub_srg.plot(width=1000, height=800)

    def get_next_point(self, reset=False):
        if reset:
            self.next_point_i = 0

        next_point = self.user_data.iloc[self.next_point_i]
        self.next_point_i += 1

        for cluster_timestamp in self.indexed_clusters.keys():
            if next_point["local_time"] >= cluster_timestamp:
                cluster_found = self.indexed_clusters[cluster_timestamp]
                del self.indexed_clusters[cluster_timestamp]

                return {"point": next_point, "centroid": cluster_centroid(cluster_found)}

        return {"point": next_point, "centroid": None}
