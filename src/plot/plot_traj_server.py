import time
import os
import random
import sys

from bokeh.layouts import column
from bokeh.models import Button
from bokeh.plotting import curdoc

from src.dao.csv_dao import load_user_gps_csv, list_user_gps_files, load_user_gps_time_window, load_user_gps_csv_by_timestamp_interval
from src.data_processment.stop_region import MovingCentroidStopRegionFinder
from src.plot.animated_plot import AnimatedPlot
from src.utils.geo import gps_loc_to_web_mercator
from src.utils.time_utils import enrich_time_columns, human_time
from src.entity.stop_region import sr_row_to_stop_region


def callback():
    point_circle = p.circle(x=[], y=[], line_color=[], size=[])
    ds_point = point_circle.data_source

    centroid_circle = p.circle(x=[], y=[], size=[], fill_alpha=[], line_alpha=[], line_color=[], line_width=[])
    ds_centroid = centroid_circle.data_source

    last_time = time.time() + period
    counter = 0

    point_sizes = []
    new_point_data = dict()
    new_centroid_data = dict()

    while counter < len(user_data):
        if time.time() - last_time >= period:
            last_time = time.time()
            counter += 1

            next = aplot.get_next_point()

            print("\n\n")
            print("weekday:", next["point"]["weekday"])
            print("hour:", next["point"]["hour"])
            print("min: ", next["point"]["min"])
            print("sec: ", next["point"]["sec"])
            print("speed:", next["point"]["speed"])

            point = next["point"]
            centroid = next["centroid"]

            point_mercator = gps_loc_to_web_mercator(lat=point["latitude"], lon=point["longitude"])

            new_point_data['x'] = ds_point.data["x"] + [point_mercator[0]]
            new_point_data['y'] = ds_point.data["y"] + [point_mercator[1]]
            new_point_data['line_color'] = ds_point.data["line_color"] + ["navy"]
            new_point_data['size'] = point_sizes + [4]

            point_sizes.append(2)

            if centroid and hilight_centroid:
                centroid_mercator = gps_loc_to_web_mercator(lat=centroid["latitude"], lon=centroid["longitude"])

                new_centroid_data["x"] = ds_centroid.data["x"] + [centroid_mercator[0]]
                new_centroid_data["y"] = ds_centroid.data["y"] + [centroid_mercator[1]]
                new_centroid_data["size"] = ds_centroid.data["size"] + [20]
                new_centroid_data["fill_alpha"] = ds_centroid.data["fill_alpha"] + [0.4]
                new_centroid_data["line_alpha"] = ds_centroid.data["line_alpha"] + [0.3]
                new_centroid_data["line_color"] = ds_centroid.data["line_color"] + ["firebrick"]
                new_centroid_data["line_width"] = ds_centroid.data["line_width"] + [1]

                ds_centroid.data = new_centroid_data

            ds_point.data = new_point_data

def plot_gps_points(userid, from_day_n, n_days, r=50, delta_t=300):
    print("LOADING USER DATA")
    print("User:", userid)
    print("From Day N:", from_day_n)
    print("N Days:", n_days)
    print("Stop Region R:", r)
    print("Stop Region Delta T:", delta_t)
    user_data = load_user_gps_csv(userid, from_day_n, n_days, fill=True)
    print("FINDING STOP REGIONS")
    clusters = MovingCentroidStopRegionFinder(region_radius=r, delta_time=delta_t).find_clusters(user_data, verbose=False)
    print(len(clusters), "found")

    return animate(userid, user_data, clusters, r, delta_t)

def plot_gps_points_by_timestamp_interval(userid, from_ts, to_ts, r=50, delta_t=300, plot2=False):
    print("LOADING USER DATA")
    print("User:", userid)
    print("From:", human_time(from_ts))
    print("N Days:", human_time(to_ts))
    print("Stop Region R:", r)
    print("Stop Region Delta T:", delta_t)

    user_data = load_user_gps_csv_by_timestamp_interval(userid, from_ts, to_ts, fill=True)
    print("FINDING STOP REGIONS")
    clusters = MovingCentroidStopRegionFinder(region_radius=r, delta_time=delta_t).find_clusters(user_data, verbose=False)
    print(len(clusters), "found")

    user_data = enrich_time_columns(user_data)
    plot_title = "USERID: " + str(userid) + " - n_CLUSTERS: " + str(len(clusters)) + " - " + "d: " + str(
        r) + ", " + "delta_t: " + str(delta_t) + \
                 " | From: " + user_data["local_datetime"].iloc[0] + \
                 " | To  : " + user_data["local_datetime"].iloc[len(user_data) - 1]

    return animate(user_data, clusters, plot_title, plot2=plot2)

def plot_gps_traj(userid, from_timestamp, to_timestamp, r=50, delta_t=300):
    print("LOADING USER DATA")
    print("User:", userid)
    print("Stop Region R:", r)
    print("Stop Region Delta T:", delta_t)

    user_data = load_user_gps_time_window(userid, from_timestamp, to_timestamp)
    user_data = enrich_time_columns(user_data)

    # print("From timestamp:", from_timestamp, user_data["local_datetime"].iloc[0])
    # print("To timestamp:", to_timestamp, user_data["local_datetime"].iloc[len(user_data) - 1])

    print("FINDING STOP REGIONS")
    clusters = MovingCentroidStopRegionFinder(region_radius=r, delta_time=delta_t).find_clusters(user_data, verbose=False)

    user_data = enrich_time_columns(user_data)
    plot_title = "USERID: " + str(userid) + " - n_CLUSTERS: " + str(len(clusters)) + " - " + "d: " + str(r) + ", " + "delta_t: " + str(delta_t) + \
    " | From: " + user_data["local_datetime"].iloc[0] + \
    " | To  : " + user_data["local_datetime"].iloc[len(user_data) - 1]

    time.sleep(3)
    return animate(user_data, clusters, plot_title)

def animate(user_data, clusters, plot_title, plot2=False, verbose=False):
    if (len(user_data) == 0):
        raise Exception("user_data is empty")

    print("PLOTTING")

    aplot = AnimatedPlot(user_data, clusters, title=plot_title)
    if not plot2:
        p = aplot.build_stop_region_plot(color="orange", circle_alpha=0.4, cluster_alpha=0.05)
    else:
        p = aplot.build_stop_region_group_quick_plot()

    # add a button widget and configure with the call back
    button_go = Button(label="Go")
    print("callback")
    button_go.on_click(callback)

    # put the button and plot in a layout and add to the document
    curdoc().add_root(column(p, button_go))

    if verbose:
        for cluster in clusters:
            print(len(cluster))
            print(cluster[["longitude", "latitude", "local_time"]])
            print("\n\n")

    hilight_centroid = not plot2
    return user_data, p, aplot, hilight_centroid


def random_user():
    user_gps_filenames = list_user_gps_files()
    filename = user_gps_filenames[random.randint(0, len(user_gps_filenames) - 1)]
    return filename.replace("_gps.csv", "")



period = 0.1 #between point plots


if __name__ == "__main__":
    os.system("PYTHONPATH=. ~/anaconda3/bin/bokeh serve --show src/plot/plot_traj_server.py")

else:
    userid = random_user()

    #user_data, p, aplot = plot_gps_points(userid=5944, r=50, delta_t=300, from_day_n=0.75, n_days=1)
    #user_data, p, aplot = plot_gps_traj(userid=6177, from_timestamp=1283536753, to_timestamp=1283587405, r=50, delta_t=300)


    user_data, p, aplot, hilight_centroid = plot_gps_points_by_timestamp_interval(userid=5928,
                                                                                  r=50,
                                                                                  delta_t=300,
                                                                                  from_ts=1253014779.0,
                                                                                  to_ts=1253363550.0 + (12*60*60),
                                                                                  plot2=True)
