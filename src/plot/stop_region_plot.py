import pandas as pd

from bokeh.plotting import figure
from bokeh.io import show
from src.utils.geo import cluster_centroid, user_data_gps_to_web_mercator, gps_loc_to_web_mercator

from bokeh.tile_providers import CARTODBPOSITRON

from src.data_processment.stop_region import MovingCentroidStopRegionFinder
from src.dao import csv_dao

def plot_stop_region(user_data, stop_region_clusters, title, color="navy", circle_alpha=0.5, cluster_alpha=0.2):
    p = plot_user_loc(user_data=user_data, title=title, color=color, alpha=circle_alpha)

    for cluster in stop_region_clusters:
        add_centroid_figure(p, cluster, cluster_alpha)

    return p

def add_centroid_figure(figure, cluster, cluster_alpha=0.5, to_mercator=True):
    centroid = cluster_centroid(cluster)

    if to_mercator:
        lon, lat = gps_loc_to_web_mercator(lat=centroid["latitude"], lon=centroid["longitude"])
        centroid_circle = figure.circle(lon, lat)
    else:
        centroid_circle = figure.circle(lon=centroid["longitude"], lat=centroid["latitude"])

    glyph = centroid_circle.glyph
    glyph.size = 20
    glyph.fill_alpha = cluster_alpha
    glyph.line_alpha = cluster_alpha
    glyph.line_color = "firebrick"
    glyph.line_dash = [6, 3]
    glyph.line_width = 1


def plot_user_loc(user_data, title, color="navy", alpha=0.5, width=800, height=800):
    tools = "pan,wheel_zoom,reset"

    p1 = gps_loc_to_web_mercator(lat=user_data["latitude"].min(), lon=user_data["longitude"].min())
    p2 = gps_loc_to_web_mercator(lat=user_data["latitude"].max(), lon=user_data["longitude"].max())

    p = figure(title=title,
               plot_width=width, plot_height=height, tools=tools,
               x_axis_type="mercator",
               y_axis_type="mercator",
               x_range=(p1[0] * 0.999, p2[0] * 1.001),
               y_range=(p1[1] * 0.999, p2[1] * 1.001))

    p.add_tile(CARTODBPOSITRON)

    mercator_loc_list = user_data_gps_to_web_mercator(user_data)

    for loc in mercator_loc_list:
        p.circle(x=loc[0], y=loc[1], size=2, alpha=alpha, color=color)

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