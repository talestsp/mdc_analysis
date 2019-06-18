import pandas as pd


def poi_types(poi_row):
    return poi_row[poi_row.notnull()].tolist()

def pois_types(pois):
    cols = pois.columns.tolist()
    del cols[cols.index("osm_id")]
    del cols[cols.index("latitude")]
    del cols[cols.index("longitude")]
    del cols[cols.index("lat_4326")]
    del cols[cols.index("lon_4326")]
    del cols[cols.index("way")]
    del cols[cols.index("name")]
    del cols[cols.index("ref")]
    del cols[cols.index("addr:housenumber")]
    del cols[cols.index("foot")]
    del cols[cols.index("building")]
    del cols[cols.index("bicycle")]
    del cols[cols.index("barrier")]
    del cols[cols.index("ele")]
    del cols[cols.index("operator")]

    return pois[cols].apply(poi_types, axis=1)


def filter_valid_pois(pois):
    columns = ["amenity", "leisure", "tourism", "shop", "historic", "sport", "building", "office",
               "access", "religion", "bicycle", "public_transport", "power", "natural",
               "man_made", "railway", "military", "place", "aerialway", "waterway"]

    valid_pois = pois[pois[columns].any(axis=1)]

    valid_pois["building_+_religion"] = valid_pois["building"] + " + " + valid_pois["religion"]

    del valid_pois["religion"]

    return valid_pois

def load_hot_osm_pois(valid_pois=False):
    '''
    Return a pandas.DataFrame with all POIs registered
    :return:
    '''
    pois = pd.read_csv("../hot_osm_analysis/outputs/planet_osm_point_full.csv")

    if valid_pois:
        pois = filter_valid_pois(pois)

    pois["types"] = pois_types(pois)
    return pois