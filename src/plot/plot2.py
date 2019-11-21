import pandas as pd

from bokeh.plotting import figure, ColumnDataSource
from bokeh.tile_providers import CARTODBPOSITRON

from src.utils import geo
from src.poi_grabber import google_places
from src.utils import time_utils

from bokeh.models import HoverTool

HOME_SR_COLOR = "lightblue"
WORK_SR_COLOR = "lightgreen"
ORDINARY_SR_COLOR = "magenta"


def stop_region_centroid_data_source(stop_regions):
    if str(type(stop_regions).__name__) == "StopRegion":
        stop_regions = [stop_regions]
    elif str(type(stop_regions).__name__) == "StopRegionGroup":
        stop_regions = stop_regions.stop_region_list

    mercator_lats = []
    mercator_lons = []
    semantics = []
    start_times = []
    end_times = []
    start_weekdays = []
    end_weekdays = []
    ids = []
    stop_region_fill_colors = []
    legends = []

    for sr in stop_regions:
        if "HOME" in sr.semantics:
            stop_region_fill_colors.append(HOME_SR_COLOR)
            legends.append(sr.semantics)

        elif "WORK" in sr.semantics:
            stop_region_fill_colors.append(WORK_SR_COLOR)
            legends.append(sr.semantics)

        else:
            stop_region_fill_colors.append(ORDINARY_SR_COLOR)
            legends.append("Stop Region")



        mercator_lon, mercator_lat = geo.gps_loc_to_web_mercator(lat=sr.centroid_lat, lon=sr.centroid_lon)
        mercator_lats.append(mercator_lat)
        mercator_lons.append(mercator_lon)

        semantics.append(sr.semantics)

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
        semantics=semantics,
        start_time=start_times,
        end_time=end_times,
        start_weekday=start_weekdays,
        end_weekday=end_weekdays,
        sr_id=ids,
        fill_color=stop_region_fill_colors,
        legend=legends
    ))

    return sr_source


def pois_data_source_from_stop_region_group(stop_region_group, n_closest_pois=30):
    pois = pd.DataFrame()
    #closest_pois = pd.DataFrame()

    for stop_region in stop_region_group.stop_region_list:
        if not stop_region.close_pois is None:
            pois = pois.append(stop_region.close_pois.head(n_closest_pois))
            #closest_pois = closest_pois.append(stop_region.closest_poi())

    pois_locs = pois.apply(lambda poi : geo.gps_loc_to_web_mercator(lat=poi["latitude"], lon=poi["longitude"]), axis=1)
    pois["lon_mercator"] = pois_locs.apply(lambda loc: loc[0])
    pois["lat_mercator"] = pois_locs.apply(lambda loc: loc[1])

    pois["show_types"] = pois["types"].apply(lambda types: str(google_places.useful_types(types)))

    pois_source = ColumnDataSource(data=dict(
        lon=pois["lon_mercator"].tolist(),
        lat=pois["lat_mercator"].tolist(),
        position=pois["position"].tolist(),
        distance=pois["distance"].tolist(),
        sr_id=pois["sr_id"].tolist(),
        show_types=pois["show_types"].tolist(),

    ))

    return pois_source



def stop_region_tooltips():
    return [
        ("sr_id", "@sr_id"),
        ("semantics", "@semantics"),
        ("start_time", "@start_time"),
        ("start_weekday", "@start_weekday"),
        ("  end_time", "@end_time"),
        ("  end_weekday", "@end_weekday")
    ]

def pois_tooltips():
    return [
        ("position", "@position"),
        ("types", "@show_types"),
        ("distance", "@distance"),
        ("sr_id", "@sr_id")
    ]

def hot_osm_pois_tooltips():
    return [
        ("types", "@types"),
        ("name", "@name")
    ]

def stop_region_mark(p, sr_source, point_color, point_size=3, fill_color="magenta", mark_type="circle",
                     fill_alpha=0.7, legend=None, tooltips=None):

    if mark_type == "circle":
        p.circle("lon", "lat", color="fill_color", size=point_size, source=sr_source, legend="legend")
        centroid_mark = p.circle("lon", "lat", color="fill_color", size=point_size, source=sr_source, fill_color="fill_color")

    elif mark_type == "square":
        p.square("lon", "lat", color="fill_color", size=point_size, source=sr_source, legend="legend")
        centroid_mark = p.square("lon", "lat", color="fill_color", size=point_size, source=sr_source, fill_color="fill_color")

    if not tooltips is None:
        p.add_tools(HoverTool(renderers=[centroid_mark], tooltips=tooltips))

    glyph = centroid_mark.glyph
    glyph.size = 20
    glyph.fill_alpha = fill_alpha
    # glyph.fill_color = fill_color
    glyph.line_alpha = fill_alpha
    glyph.line_color = "firebrick"
    glyph.line_dash = [6, 3]
    glyph.line_width = 1

    return p

def poi_mark(p, poi_source, point_color="navy", point_size=3, mark_type="circle", alpha=0.7, tooltips=pois_tooltips()):

    if mark_type == "circle":
        poi_mark = p.circle("lon", "lat", color=point_color, size=point_size, source=poi_source, alpha=alpha, legend="pois_google")

    p.add_tools(HoverTool(renderers=[poi_mark], tooltips=tooltips))

    return p

def centroids_figure_mouseover(stop_region_group, p, legend="stop region", point_color="magenta", mark_type="circle",
                              point_size=3, fill_color="magenta", fill_alpha=0.3):

    sr_source = stop_region_centroid_data_source(stop_region_group)
    tooltips = stop_region_tooltips()

    p = stop_region_mark(p=p, sr_source=sr_source, point_color=point_color, point_size=point_size, mark_type=mark_type,
                         fill_color=fill_color, fill_alpha=fill_alpha, legend=legend, tooltips=tooltips)
    return p

def pois_figure_mouseover(data_source, color="navy", alpha=0.7, point_size=3, mark_type="circle", p=None):
    tooltips = pois_tooltips()

    p = poi_mark(p=p, poi_source=data_source, point_color=color, point_size=point_size, mark_type=mark_type,
                         alpha=alpha, tooltips=tooltips)

    return p

def plot_stop_region_mousover(stop_region_obj, title="", width=800, height=600, p=None, mark_type="circle"):
    if p is None:
        p = mercator_fig(title=title, width=width, height=height)

    p = centroids_figure_mouseover(stop_region_obj, p, mark_type=mark_type)
    return p

def plot_stop_region(stop_region_obj, title="", color="magenta", width=800, height=600, legend=None, p=None, mark_type="circle"):
    if p is None:
        p = mercator_fig(title=title, width=width, height=height)

    sr_source = stop_region_centroid_data_source(stop_region_obj)

    p = stop_region_mark(p, sr_source, point_color=color, point_size=3, fill_color=color, mark_type=mark_type,
                     fill_alpha=0.4, legend=legend, tooltips=None)

    return p

def plot_stop_region_group(stop_region_group, title="", fill_color="magenta", mark_type="circle",
                           width=800, height=600, p=None, plot_n_pois=30, point_size=6):
    if p is None:
        p = mercator_fig(title=title, width=width, height=height)

    p = centroids_figure_mouseover(stop_region_group, fill_color=fill_color, p=p, mark_type=mark_type)

    pois_data_source = pois_data_source_from_stop_region_group(stop_region_group, n_closest_pois=plot_n_pois)

    p = pois_figure_mouseover(data_source=pois_data_source, color="navy", alpha=0.7, point_size=point_size, p=p)

    p = hilight_closest_poi(stop_region_group, p=p, point_size=10)

    return p

def hilight_closest_poi(stop_region_group, p, color="red", alpha=0.25, point_size=8):
    closests_pois = pd.DataFrame()

    for sr in stop_region_group.stop_region_list:
        closests_pois = closests_pois.append(sr.closest_poi())

    pois_locs = closests_pois.apply(lambda poi: geo.gps_loc_to_web_mercator(lat=poi["latitude"], lon=poi["longitude"]),axis=1)

    lons_mercator = pois_locs.apply(lambda loc: loc[0])
    lats_mercator = pois_locs.apply(lambda loc: loc[1])

    p.square(lons_mercator, lats_mercator, color=color, size=point_size, alpha=alpha, legend="closest_pois")

    return p

def add_hot_osm_pois(pois, p, color="orange", alpha=0.7, size=7):
    data_source = hot_osm_data_source(pois)
    p = hot_osm_pois_figure_mouseover(data_source=data_source, color=color, alpha=alpha, point_size=size, p=p)

    return p

def hot_osm_data_source(pois):
    pois = pois.copy(deep=True)
    pois_locs = pois.apply(lambda poi: geo.gps_loc_to_web_mercator(lat=poi["lat_4326"], lon=poi["lon_4326"]), axis=1)
    pois["lon_mercator"] = pois_locs.apply(lambda loc: loc[0])
    pois["lat_mercator"] = pois_locs.apply(lambda loc: loc[1])

    return ColumnDataSource(data=dict(
        lon=pois["lon_mercator"].tolist(),
        lat=pois["lat_mercator"].tolist(),
        name=pois["name"].tolist(),
        types=pois["types"].tolist(),
    ))

def hot_osm_pois_figure_mouseover(data_source, color="orange", alpha=0.3, point_size=3, p=None):
    poi_mark = p.triangle("lon", "lat", color=color, size=point_size, source=data_source, alpha=alpha,
                          legend="hot_osm_pois")

    p.add_tools(HoverTool(renderers=[poi_mark], tooltips=hot_osm_pois_tooltips()))

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

def mark_home_and_work(plot, sr_group, home_color="lightblue", work_color="lightgreen"):
    for sr in sr_group.stop_region_list:
        if "HOME" in sr.semantics:
            plot = sr.plot_simple(p=plot, color=home_color, legend="HOME")

        if "WORK" in sr.semantics:
            plot = sr.plot_simple(p=plot, color=work_color, legend="WORK")
    return plot