from src.plot.stop_region_plot import plot_stop_region, plot_user_loc

class AnimatedPlot:

    def __init__(self, user_data, clusters, title):
        self.user_data = user_data
        self.title = title
        self.next_point_i = 0

        self.indexed_clusters = {}

        for cluster in clusters:
            cluster = cluster.sort_values(by="time")
            self.indexed_clusters[cluster.tail(1).index.name] = cluster


    def build_base_plot(self, color="navy", alpha=0.2):
        return plot_user_loc(self.user_data, self.title, color=color, alpha=alpha)

    def get_next_point(self, reset=False):
        if reset:
            self.next_point_i = 0

        next_point = self.user_data.iloc[self.next_point_i]
        self.next_point_i += 1

        if next_point.name in self.indexed_clusters:
            return {"point": next_point, "cluster": self.indexed_clusters[next_point.name]}
        else:
            return {"point": next_point}
