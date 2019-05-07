import pandas as pd

from bokeh.plotting import figure
from bokeh.io import show
from bokeh.tile_providers import CARTODBPOSITRON

from src.utils.geo import cluster_centroid, user_data_gps_to_web_mercator, gps_loc_to_web_mercator
from src.utils.color_utils import pick_random_color
from src.dao import csv_dao
from src.plot import poi_plot

def plot_stop_region_with_trajectory(user_data, stop_region_clusters, title, color="navy", circle_alpha=0.5, cluster_alpha=0.2):
    p = plot_user_loc(user_data=user_data, title=title, color=color, alpha=circle_alpha)

    for cluster in stop_region_clusters:
        add_centroid_figure(p, cluster=cluster, cluster_alpha=cluster_alpha)

    return p

def plot_stop_regions(clusters, title, width=800, height=600, plot_points=False, same_color=True):
    p = mercator_fig(title, point_mercator1=None, point_mercator2=None, width=width, height=height)

    if same_color:
        color = pick_random_color()

    for cluster in clusters:
        if not same_color:
            color = pick_random_color()

        add_centroid_figure(p, cluster, fill_color=color)

        if plot_points:
            mercator_loc_list = user_data_gps_to_web_mercator(cluster)
            for loc in mercator_loc_list:
                p.circle(x=loc[0], y=loc[1], size=2, alpha=0.3, color=color)

    return p


def add_centroid_figure(figure, cluster, legend=None, point_color="magenta", point_size=3, fill_color="magenta", cluster_alpha=0.3, to_mercator=True):
    centroid = cluster_centroid(cluster)
    add_calculated_centroid_figure(figure, centroid, legend, point_color, point_size, fill_color, cluster_alpha, to_mercator)

def add_calculated_centroid_figure(figure, centroid, legend=None, point_color="magenta", point_size=3, fill_color="magenta", cluster_alpha=0.3, to_mercator=True):
    if to_mercator:
        lon, lat = gps_loc_to_web_mercator(lat=centroid["latitude"], lon=centroid["longitude"])
        centroid_circle = figure.circle(lon, lat)
    else:
        centroid_circle = figure.circle(lon=centroid["longitude"], lat=centroid["latitude"])

    centroid_mercator = gps_loc_to_web_mercator(centroid["latitude"], centroid["longitude"])

    if legend is None:
        figure.circle(centroid_mercator[0], centroid_mercator[1], color=point_color, size=point_size)
    else:
        figure.circle(centroid_mercator[0], centroid_mercator[1], color=point_color, size=point_size, legend=legend)

    glyph = centroid_circle.glyph
    glyph.size = 20
    glyph.fill_alpha = cluster_alpha
    glyph.fill_color = fill_color
    glyph.line_alpha = cluster_alpha
    glyph.line_color = "firebrick"
    glyph.line_dash = [6, 3]
    glyph.line_width = 1

def plot_users_stop_region(users, width=1500, height=800):
    p = mercator_fig(title="Users: " + str(users), width=width, height=height)
    for user in users:
        add_users_stop_region(user, p)

    return p

def add_users_stop_region(user, figure):
    clusters = csv_dao.load_user_stop_regions(user)
    for cluster in clusters:
        add_centroid_figure(figure, cluster=cluster, cluster_alpha=0.2)

    return figure

def plot_user_loc(user_data, title, color="navy", alpha=0.5, width=1500, height=800, size=2, p=None, legend=None):
    '''
    Plots user locations
    :param user_data:
    :param title:
    :param color:
    :param alpha:
    :param width:
    :param height:
    :return:
    '''
    p1 = gps_loc_to_web_mercator(lat=user_data["latitude"].min(), lon=user_data["longitude"].min())
    p2 = gps_loc_to_web_mercator(lat=user_data["latitude"].max(), lon=user_data["longitude"].max())

    if p is None:
        p = mercator_fig(title=title, point_mercator1=p1, point_mercator2=p2, width=width, height=height)

    mercator_loc_list = user_data_gps_to_web_mercator(user_data)

    for loc in mercator_loc_list:
        p.circle(x=loc[0], y=loc[1], size=size, alpha=alpha, color=color, legend=legend)

    return p

def mercator_fig(title, point_mercator1=None, point_mercator2=None, width=1500, height=800):
    tools = "pan,wheel_zoom,reset"

    if point_mercator1 is None and point_mercator2 is None:
        p = figure(title=title,
                   plot_width=width, plot_height=height, tools=tools,
                   x_axis_type="mercator",
                   y_axis_type="mercator")

    else:
        p = figure(title=title,
                   plot_width=width, plot_height=height, tools=tools,
                   x_axis_type="mercator",
                   y_axis_type="mercator",
                   x_range=(point_mercator1[0] * 0.999, point_mercator2[0] * 1.001),
                   y_range=(point_mercator1[1] * 0.999, point_mercator2[1] * 1.001))

    p.add_tile(CARTODBPOSITRON)

    return p

def plot_point(figure, lat, lon, alpha=0.5, color="magenta", conver_to_mercator=True):
    if conver_to_mercator:
        lat, lon = gps_loc_to_web_mercator(lat, lon)

    figure.circle(x=lat, y=lon, size=4, alpha=alpha, color=color)
    return figure


if __name__ == "__main__":
    #pd.set_option('display.max_columns', None)
    #pd.set_option('display.width', 1000)
    #pd.set_option('display.float_format', lambda x: '%.3f' % x)

    #p = plot_point(mercator_fig(title=""), lat=45.739885, lon=5.7493075000000005)
    #p = plot_point(p, lat=47.790615, lon=10.6232425)

    #p = plot_point(p, lat=47.277932500000006, lon=9.40475875, color="blue")
    #p = plot_point(p, lat=47.277932500000006, lon=6.96779125, color="blue")
    #p = plot_point(p, lat=46.2525675, lon=6.96779125, color="blue")
    #p = plot_point(p, lat=46.2525675, lon=9.40475875, color="blue")

    #p = plot_point(p, lat=46.76525, lon=8.186275, color="orange")

    #p = plot_point(p, lat=46.124396875, lon=6.6631703125, color="red")
    #p = plot_point(p, lat=46.124396875, lon=6.053928437500001, color="red")
    #p = plot_point(p, lat=45.868055625, lon=6.053928437500001, color="red")
    #p = plot_point(p, lat=45.868055625, lon=6.6631703125, color="red")

    #show(p)

    # plot_stop_regions_and_pois()

    # r = 50
    # delta_t = 300
    #
    #
    # for userid in [6171]:#[6171, 6033]:
    #     user_data = csv_dao.load_user_gps_csv(userid, 0, 1)
    #     stop_region_finder = MovingCentroidStopRegionFinder(region_radius=r, delta_time=delta_t)
    #     clusters = stop_region_finder.find_clusters(user_data)
    #     show(plot_stop_region_with_trajectory(user_data, clusters, title="USERID: " + str(userid) + " - n_CLUSTERS: " + str(len(clusters)) + " - " + "d: " + str(r) + ", " + "delta_t: " + str(delta_t)))

    pass