# myapp.py

import time

from bokeh.layouts import column
from bokeh.models import Button
from bokeh.palettes import RdYlBu3
from bokeh.plotting import figure, curdoc

from src.dao.csv_dao import load_user_gps_csv
from src.data_processment.stop_region import MovingCentroidStopRegionFinder
from src.plot.animated_plot import AnimatedPlot

user_data = load_user_gps_csv(6171, 0, 1)
clusters = MovingCentroidStopRegionFinder(region_radius=50, delta_time=300).find_clusters(user_data, verbose=True)

aplot = AnimatedPlot(user_data, clusters, "Animated Plot")
p = aplot.build_base_plot(color="orange", alpha=0.5)

head_circle = p.circle(x=[], y=[], line_color=[], size=[])

ds = head_circle.data_source

def callback():
    period = 0.005
    last_time = time.time() + period
    counter = 0

    sizes = []
    new_data = dict()

    while counter < len(user_data):
        if time.time() - last_time >= period:
            last_time = time.time()
            counter += 1

            point = aplot.get_next_point()["point"]

            new_data['x'] = ds.data["x"] + [point["longitude"]]
            new_data['y'] = ds.data["y"] + [point["latitude"]]
            new_data['line_color'] = ds.data["line_color"] + ["navy"]
            new_data['size'] = sizes + [4]

            sizes.append(2)

            ds.data = new_data



# add a button widget and configure with the call back
button = Button(label="Go")
button.on_click(callback)

# put the button and plot in a layout and add to the document
curdoc().add_root(column(p, button))

