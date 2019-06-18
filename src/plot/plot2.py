import pandas as pd

from bokeh.plotting import figure, ColumnDataSource
from bokeh.tile_providers import CARTODBPOSITRON

from src.utils import geo
from src.utils.color_utils import pick_random_color
from src.utils import time_utils

from bokeh.models import HoverTool


def stop_region_centroid_data_source(stop_regions):
    if str(type(stop_regions).__name__) == "StopRegion":
        stop_regions = [stop_regions]
    elif str(type(stop_regions).__name__) == "StopRegionSequence":
        stop_regions = stop_regions.stop_region_sequence

    mercator_lats = []
    mercator_lons = []
    start_times = []
    end_times = []
    start_weekdays = []
    end_weekdays = []
    ids = []

    for sr in stop_regions:
        mercator_lon, mercator_lat = geo.gps_loc_to_web_mercator(lat=sr.centroid_lat, lon=sr.centroid_lon)
        mercator_lats.append(mercator_lat)
        mercator_lons.append(mercator_lon)

        start_human_datetime = time_utils.human_time(sr.start_time)
        end_human_datetime = time_utils.human_time(sr.end_time)

        start_times.append(start_human_datetime["datetime"])
        end_times.append(end_human_datetime["datetime"])
        start_weekdays.append(start_human_datetime["weekday"])
        end_weekdays.append(end_human_datetime["weekday"])

        ids.append(sr.sr_id)

    sr_source = ColumnDataSource(data=dict(
        lon=mercator_lons,
        lat=mercator_lats,
        start_time=start_times,
        end_time=end_times,
        start_weekday=start_weekdays,
        end_weekday=end_weekdays,
        sr_id=ids
    ))

    return sr_source


def stop_region_tooltips():
    return [
        ("sr_id", "@sr_id"),
        ("start_time", "@start_time"),
        ("start_weekday", "@start_weekday"),
        ("  end_time", "@end_time"),
        ("  end_weekday", "@end_weekday")
    ]

def stop_region_mark(p, sr_source, point_color, point_size=3, fill_color="magenta", mark_type="circle",
                     fill_alpha=0.4, legend=None, tooltips=None):

    print("mark_type", mark_type)

    if mark_type == "circle":
        p.circle("lon", "lat", color=point_color, size=point_size, source=sr_source, legend=legend)
        centroid_mark = p.circle("lon", "lat", color=point_color, size=point_size, source=sr_source)
        p.add_tools(HoverTool(renderers=[centroid_mark], tooltips=tooltips))

    elif mark_type == "square":
        p.square("lon", "lat", color=point_color, size=point_size, source=sr_source, legend=legend)
        centroid_mark = p.square("lon", "lat", color=point_color, size=point_size, source=sr_source)
        p.add_tools(HoverTool(renderers=[centroid_mark], tooltips=tooltips))

    glyph = centroid_mark.glyph
    glyph.size = 20
    glyph.fill_alpha = fill_alpha
    glyph.fill_color = fill_color
    glyph.line_alpha = fill_alpha
    glyph.line_color = "firebrick"
    glyph.line_dash = [6, 3]
    glyph.line_width = 1

    return p

def centroids_figure_mouseover(stop_region_sequence, p, legend=None, point_color="magenta", mark_type="circle",
                              point_size=3, fill_color="magenta", fill_alpha=0.3):

    sr_source = stop_region_centroid_data_source(stop_region_sequence)
    tooltips = stop_region_tooltips()

    p = stop_region_mark(p=p, sr_source=sr_source, point_color=point_color, point_size=point_size, mark_type=mark_type,
                         fill_color=fill_color, fill_alpha=fill_alpha, legend=legend, tooltips=tooltips)
    return p

def plot_stop_region(stop_region_obj, title="", width=800, height=600, p=None, mark_type="circle"):
    if p is None:
        p = mercator_fig(title=title, width=width, height=height)

    p = centroids_figure_mouseover(stop_region_obj, p, mark_type=mark_type)
    return p

def plot_stop_region_sequence(stop_region_sequence, title="", fill_color="magenta", mark_type="circle",
                              width=800, height=600, p=None):
    if p is None:
        p = mercator_fig(title=title, width=width, height=height)

    p = centroids_figure_mouseover(stop_region_sequence, fill_color=fill_color, p=p, mark_type=mark_type)
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