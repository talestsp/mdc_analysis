import pandas as pd

from bokeh.plotting import figure
from bokeh.layouts import gridplot
from bokeh.io import output_notebook, show

from src.data_processment.stop_region import stop_regions

DAY_SECONDS = 86400

class StopRegionPlot:

    def __init__(self, userid, from_day_n, to_day_n):

        user_data = pd.read_csv("outputs/user_gps/" + str(userid) + '_gps.csv').drop_duplicates().sort_values(by="time")
        min_time = user_data["time"].min()
        use_data_from_time = min_time + DAY_SECONDS * from_day_n
        use_data_to_time = use_data_from_time + to_day_n * DAY_SECONDS

        self.user_data = user_data[(user_data["time"] >= use_data_from_time) & (user_data["time"] <= use_data_to_time)]

    def plot_stop_region(self, stop_region_clusters, title):
        p = self.plot_user_loc(title=title)

        for cluster in stop_region_clusters:
            centroid = self.cluster_centroid(cluster)

            centroid_circle = p.circle(centroid["longitude"], centroid["latitude"])

            glyph = centroid_circle.glyph
            glyph.size = 20
            glyph.fill_alpha = 0.2
            glyph.line_color = "firebrick"
            glyph.line_dash = [6, 3]
            glyph.line_width = 1

        return p


    def plot_user_loc(self, title, color="navy", width=800, height=800):
        tools = "pan,wheel_zoom,reset"
        p = figure(plot_width=width, plot_height=height, tools=tools, title=title)
        p.circle(self.user_data["longitude"], self.user_data["latitude"], size=2, alpha=0.5, color=color)

        return p

    def cluster_centroid(self, cluster):
        length = len(cluster)
        sum_lat = cluster["latitude"].sum()
        sum_lon = cluster["longitude"].sum()
        points_centroid = {"latitude": sum_lat / length, "longitude": sum_lon / length}
        return points_centroid

    # def distance_to_degrees(self):
    #     a = sin²(Δφ / 2) + cos(φ1).cos(φ2).sin²(Δλ / 2)
    #     c = 2.atan2(√a, √(1−a))
    #     d = R.c
    #     d


if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    pd.set_option('display.float_format', lambda x: '%.3f' % x)


    srp = StopRegionPlot(6171, 0, 1)

    # show(srp.plot_user_loc())

    delta_t=300


    for d in [50]:
        clusters = stop_regions(srp.user_data, d=d, delta_t=delta_t)
        show(srp.plot_stop_region(clusters, title="n_CLUSTERS: " + str(len(clusters)) + " - " + "d: " + str(d) + ", " + "delta_t: " + str(delta_t)))