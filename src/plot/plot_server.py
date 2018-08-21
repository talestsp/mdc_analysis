import time
import os

from bokeh.layouts import column
from bokeh.models import Button
from bokeh.palettes import RdYlBu3
from bokeh.plotting import figure, curdoc

from src.dao.csv_dao import load_user_gps_csv
from src.data_processment.stop_region import MovingCentroidStopRegionFinder
from src.plot.animated_plot import AnimatedPlot
from src.utils.geo import gps_loc_to_web_mercator


def callback():
    point_circle = p.circle(x=[], y=[], line_color=[], size=[])
    ds_point = point_circle.data_source

    centroid_circle = p.circle(x=[], y=[], size=[], fill_alpha=[], line_alpha=[], line_color=[], line_width=[])
    ds_centroid = centroid_circle.data_source

    period = 0.01
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

            point = next["point"]
            centroid = next["centroid"]

            point_mercator = gps_loc_to_web_mercator(lat=point["latitude"], lon=point["longitude"])

            new_point_data['x'] = ds_point.data["x"] + [point_mercator[0]]
            new_point_data['y'] = ds_point.data["y"] + [point_mercator[1]]
            new_point_data['line_color'] = ds_point.data["line_color"] + ["navy"]
            new_point_data['size'] = point_sizes + [4]

            point_sizes.append(2)

            if not centroid is None:
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
    user_data = load_user_gps_csv(userid, from_day_n, n_days)
    print("FINDING STOP REGIONS")
    clusters = MovingCentroidStopRegionFinder(region_radius=r, delta_time=delta_t).find_clusters(user_data, verbose=False)
    print("PLOTTING")

    aplot = AnimatedPlot(user_data, clusters, title="USERID: " + str(userid) + " - n_CLUSTERS: " + str(len(clusters)) + " - " + "d: " + str(r) + ", " + "delta_t: " + str(delta_t))
    p = aplot.build_stop_region_plot(color="orange", circle_alpha=0.4, cluster_alpha=0.05)

    # add a button widget and configure with the call back
    button_go = Button(label="Go")
    button_go.on_click(callback)

    # put the button and plot in a layout and add to the document
    curdoc().add_root(column(p, button_go))

    return user_data, p, aplot


user_data, p, aplot = plot_gps_points(userid=6171, r=50, delta_t=300, from_day_n=0, n_days=1)

if __name__ == "__main__":
    os.system("PYTHONPATH=. ~/anaconda3/bin/bokeh serve --show src/plot/plot_server.py")

