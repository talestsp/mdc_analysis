import pandas as pd
from src.utils import geo
from src.dao import csv_dao


def same_closest_poi(last_sr, sr):
    set_sr_pois = set(sr.closest_poi()["place_id"].tolist())
    set_last_sr_pois = set(last_sr.closest_poi()["place_id"].tolist())
    return len(set_sr_pois.intersection(set_last_sr_pois)) > 0

def close_sr_short_time(last_sr, sr, time_tolerance_secs=600, distance_tolerance_m=5):
    return sr.distance_to_another_sr(last_sr) <= distance_tolerance_m and sr.delta_time_to_another_sr(
        last_sr) <= time_tolerance_secs

def agglutinate(stop_regions):
        end_times = []
        start_times = []
        user_ids = []
        semantics = []
        gps_points = pd.DataFrame()

        early_time_sr = stop_regions[0]

        for sr in stop_regions:
            end_times.append(sr.end_time)
            start_times.append(sr.start_time)
            user_ids.append(sr.user_id)
            semantics = semantics + sr.semantics
            gps_points = gps_points.append(csv_dao.load_stop_region_by_sr_id(sr.user_id, sr.sr_id))[["latitude", "longitude"]]

            if sr.start_time < early_time_sr.start_time:
                early_time_sr = sr

        centroid = geo.cluster_centroid(gps_points)

        return {'centroid_lat': centroid["latitude"],
                'centroid_lon': centroid["longitude"],
                'start_time': pd.Series(start_times).min(),
                'end_time': pd.Series(end_times).max(),
                'sr_id': "agg_{}".format(early_time_sr.sr_id),
                'user_id': early_time_sr.user_id,
                'semantics': pd.Series(semantics).drop_duplicates().tolist(),
                'agglutination': stop_regions}

def agglutinate_consecutive_stop_regions(sr_sequence, agglutination_rule):
    agglutinate = [[sr_sequence[0]]]
    agglutination_report = []

    last_sr = sr_sequence[0]
    for sr in sr_sequence[1:]:
        agglutination_report_row = {"distance": round(sr.distance_to_another_sr(last_sr), 1),
                                    "delta_t": sr.delta_time_to_another_sr(last_sr),
                                    "last_sr": last_sr.sr_id, "last_sr_tag": last_sr.tag_closest_poi(),
                                    "sr": sr.sr_id, "sr_tag": sr.tag_closest_poi(),
                                    "last_sr_semantics": last_sr.semantics,
                                    "sr_semantics": sr.semantics}

        if agglutination_rule(last_sr, sr):
            agglutinate[-1].append(sr)
            agglutination_report_row["agglutinate"] = True

        else:
            agglutinate.append([sr])
            agglutination_report_row["agglutinate"] = False

        agglutination_report.append(agglutination_report_row)
        last_sr = sr

    return agglutinate, pd.DataFrame(agglutination_report)[
        ["agglutinate", "delta_t", "distance", "last_sr_tag", "sr_tag", "last_sr_semantics", "sr_semantics"]]
