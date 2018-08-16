import pandas as pd

from bokeh.plotting import figure
from bokeh.io import show
from src.utils.geo import cluster_centroid

from src.data_processment.stop_region import MovingCentroidStopRegionFinder
from src.dao import csv_dao

def plot_stop_region(user_data, stop_region_clusters, title, color="navy", circle_alpha=0.5, cluster_alpha=0.2):
    p = plot_user_loc(user_data=user_data, title=title, color=color, alpha=circle_alpha)

    for cluster in stop_region_clusters:
        add_centroid_figure(p, cluster, cluster_alpha)

    return p

def add_centroid_figure(figure, cluster, cluster_alpha=0.5):
    centroid = cluster_centroid(cluster)

    centroid_circle = figure.circle(centroid["longitude"], centroid["latitude"])

    glyph = centroid_circle.glyph
    glyph.size = 20
    glyph.fill_alpha = cluster_alpha
    glyph.line_alpha = cluster_alpha
    glyph.line_color = "firebrick"
    glyph.line_dash = [6, 3]
    glyph.line_width = 1


def plot_user_loc(user_data, title, color="navy", alpha=0.5, width=800, height=800):
    tools = "pan,wheel_zoom,reset"
    p = figure(plot_width=width, plot_height=height, tools=tools, title=title)
    p.circle(user_data["longitude"], user_data["latitude"], size=2, alpha=alpha, color=color)

    return p

if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    pd.set_option('display.float_format', lambda x: '%.3f' % x)

    r = 50
    delta_t = 300


    for userid in [6171]:#[6171, 6033]:
        user_data = csv_dao.load_user_gps_csv(userid, 0, 1)
        stop_region_finder = MovingCentroidStopRegionFinder(region_radius=r, delta_time=delta_t)
        clusters = stop_region_finder.find_clusters(user_data)
        show(plot_stop_region(user_data, clusters, title="USERID: " + str(userid) + " - n_CLUSTERS: " + str(len(clusters)) + " - " + "d: " + str(r) + ", " + "delta_t: " + str(delta_t)))