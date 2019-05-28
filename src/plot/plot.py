import pandas as pd

from bokeh.plotting import figure
from bokeh.io import show
from bokeh.tile_providers import CARTODBPOSITRON

from src.utils.geo import cluster_centroid, user_data_gps_to_web_mercator, gps_loc_to_web_mercator
from src.utils.color_utils import pick_random_color
from src.dao import csv_dao

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
            mercator_loc_df = pd.DataFrame(user_data_gps_to_web_mercator(cluster))
            p.circle(x=mercator_loc_df[0], y=mercator_loc_df[1], size=2, alpha=0.3, color=color)

    return p


def plot_stop_regions_centroids(centroids, title="", lat_col="latitude", lon_col="longitude", width=800, height=600,
                                fill_color=pick_random_color(), legend=None, p=None):
    if p is None:
        p = mercator_fig(title, point_mercator1=None, point_mercator2=None, width=width, height=height)

    for index, centroid in centroids.iterrows():
        add_calculated_centroid_figure(p, centroid, lat_col=lat_col, lon_col=lon_col, point_color="magenta",
                                       point_size=3, fill_color=fill_color, cluster_alpha=0.3, to_mercator=True,
                                       legend=legend)

    return p


def plot_stop_regions_centroids3(centroids, title="", lat_col="latitude", lon_col="longitude", width=800, height=600,
                                fill_color=pick_random_color(), legend=None, p=None, mark="circle"):
    if p is None:
        p = mercator_fig(title, point_mercator1=None, point_mercator2=None, width=width, height=height)

    return add_calculated_centroids_figure(p, centroids, lat_col=lat_col, lon_col=lon_col, point_color=fill_color,
                                       point_size=3, fill_color=fill_color, cluster_alpha=0.3, to_mercator=True,
                                       legend=legend, mark=mark)


def plot_stop_regions_centroids2(centroids, title="", lat_col="latitude", lon_col="longitude", width=800, height=600,
                                 fill_color=pick_random_color(), legend=None, p=None):
    if p is None:
        p = mercator_fig(title, point_mercator1=None, point_mercator2=None, width=width, height=height)

    centroids.apply(
        lambda row: add_calculated_centroid_figure(p, row, lat_col=lat_col, lon_col=lon_col, point_color=fill_color,
                                                   point_size=3, fill_color=fill_color, cluster_alpha=0.3,
                                                   to_mercator=True, legend=legend), axis=1)

    return p


def plot_poi(data, title, lat_col="latitude", lon_col="longitude", width=800, height=600, color=pick_random_color(), figure=None):
    if figure is None:
        figure = mercator_fig(title, point_mercator1=None, point_mercator2=None, width=width, height=height)

    mercator_loc_df = pd.DataFrame(user_data_gps_to_web_mercator(data, lat_col=lat_col, lon_col=lon_col))
    figure.circle(x=mercator_loc_df[0], y=mercator_loc_df[1], size=5, alpha=0.3, color=color)

    return figure

def add_centroid_figure(figure, cluster, legend=None, point_color="magenta", point_size=3, fill_color="magenta",
                        cluster_alpha=0.3, to_mercator=True):
    centroid = cluster_centroid(cluster)
    add_calculated_centroid_figure(figure, centroid, legend=legend, point_color=point_color, point_size=point_size,
                                   fill_color=fill_color, cluster_alpha=cluster_alpha, to_mercator=to_mercator)

def add_calculated_centroid_figure(figure, centroid, lat_col="latitude", lon_col="longitude", legend=None,
                                   point_color="magenta", point_size=3, fill_color="magenta", cluster_alpha=0.3,
                                   to_mercator=True):

    if to_mercator:
        lon, lat = gps_loc_to_web_mercator(lat=centroid[lat_col], lon=centroid[lon_col])
        centroid_circle = figure.circle(lon, lat)
    else:
        centroid_circle = figure.circle(lon=centroid[lon_col], lat=centroid[lat_col])

    centroid_mercator = gps_loc_to_web_mercator(centroid[lat_col], centroid[lon_col])

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

def add_calculated_centroids_figure(figure, centroids, lat_col="latitude", lon_col="longitude", legend=None,
                                   point_color="magenta", point_size=3, fill_color="magenta", cluster_alpha=0.3,
                                   to_mercator=True, mark="circle"):


    if mark == "circle":
        mark = figure.circle
    elif mark == "square":
        mark = figure.square
    else:
        mark = figure.circle = figure.circle

    if to_mercator:
        locs = centroids.apply(lambda centroid : gps_loc_to_web_mercator(lat=centroid[lat_col], lon=centroid[lon_col]), axis=1)
        lons_mercator = locs.apply(lambda loc: loc[0])
        lats_mercator = locs.apply(lambda loc: loc[1])

        mark(lons_mercator, lats_mercator, size=20, color=point_color, alpha=cluster_alpha,
                        fill_color=fill_color, legend=legend)
        mark(lons_mercator, lats_mercator, color=point_color, size=point_size)
    else:
        mark(centroids[lon_col], centroids[lat_col], size=20, color=point_color, alpha=cluster_alpha,
                        fill_color=fill_color, legend=legend)

        mark(lon=centroids[lon_col], lat=centroids[lat_col])

    return figure


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

def plot_user_loc(user_data, lat_col="latitude", lon_col="longitude", title="", color="navy", alpha=0.5, width=1500, height=800, size=2, p=None, legend=None):
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

    p1 = gps_loc_to_web_mercator(lat=user_data[lat_col].min(), lon=user_data[lon_col].min())
    p2 = gps_loc_to_web_mercator(lat=user_data[lat_col].max(), lon=user_data[lon_col].max())

    if p is None:
        p = mercator_fig(title=title, point_mercator1=p1, point_mercator2=p2, width=width, height=height)

    mercator_loc_df = pd.DataFrame(user_data_gps_to_web_mercator(user_data, lat_col=lat_col, lon_col=lon_col))

    p.circle(x=mercator_loc_df[0], y=mercator_loc_df[1], size=size, alpha=alpha, color=color, legend=legend)

    return p

def plot_user_loc_bkp(user_data, title, color="navy", alpha=0.5, width=1500, height=800, size=2, p=None, legend=None):
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

    print(mercator_loc_list)

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
