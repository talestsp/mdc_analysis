import pandas as pd

from bokeh.plotting import figure
from bokeh.layouts import gridplot
from bokeh.io import output_notebook, show

from src.data_processment.stop_region import MovingCentroidStopRegionFinder
from src.dao import csv_dao

def plot_stop_region(user_data, stop_region_clusters, title):
    p = plot_user_loc(user_data=user_data, title=title)

    for cluster in stop_region_clusters:
        print("CLUSTER")
        print(cluster)
        print()
        centroid = cluster_centroid(cluster)

        centroid_circle = p.circle(centroid["longitude"], centroid["latitude"])

        glyph = centroid_circle.glyph
        glyph.size = 20
        glyph.fill_alpha = 0.2
        glyph.line_color = "firebrick"
        glyph.line_dash = [6, 3]
        glyph.line_width = 1

    return p


def plot_user_loc(user_data, title, color="navy", width=800, height=800):
    tools = "pan,wheel_zoom,reset"
    p = figure(plot_width=width, plot_height=height, tools=tools, title=title)
    p.circle(user_data["longitude"], user_data["latitude"], size=2, alpha=0.5, color=color)

    return p

def cluster_centroid(cluster):
    length = len(cluster)
    sum_lat = cluster["latitude"].sum()
    sum_lon = cluster["longitude"].sum()
    points_centroid = {"latitude": sum_lat / length, "longitude": sum_lon / length}
    return points_centroid

if __name__ == "__main__":
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    pd.set_option('display.float_format', lambda x: '%.3f' % x)

    r = 50
    delta_t = 300


    for userid in [6033]:#[6171, 6033]:
        user_data = csv_dao.load_user_gps_csv(userid, 0, 1)
        stop_region_finder = MovingCentroidStopRegionFinder(region_radius=r, delta_time=delta_t)
        clusters = stop_region_finder.find_clusters(user_data)
        show(plot_stop_region(user_data, clusters, title="USERID: " + str(userid) + " - n_CLUSTERS: " + str(len(clusters)) + " - " + "d: " + str(r) + ", " + "delta_t: " + str(delta_t)))