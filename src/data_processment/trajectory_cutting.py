import pandas as pd
import numpy as np
import copy

def gaps_params(user_gps_data, gap_tresh_minutes):
    '''
    Returns a pd.DataFrame with gaps parameters
    :param user_gps_data:
    :param gap_tresh_minutes:
    :return:
    '''
    gaps_data = gap_missing_values(user_gps_data).to_frame().reset_index().rename({0: "gap_time_sec", "index": "stop"},
                                                                                  axis=1)
    gaps_data["start"] = [None] + gaps_data.iloc[0: len(gaps_data) - 1]["stop"].tolist()
    gaps_data["start"] = gaps_data["start"].replace({np.NaN: None})

    selected_gaps = copy.deepcopy(gaps_data[gaps_data["gap_time_sec"] >= gap_tresh_minutes * 60])

    selected_gaps["user_id"] = user_gps_data["userid"].drop_duplicates().item()

    return selected_gaps[["user_id", "gap_time_sec", "start", "stop"]]

def cut_traj_in_trips(srg_sequence_report, gaps):
    srg_sequence_report = srg_sequence_report.sort_values(by="sr_start_time")

    trips = [ [] ]
    previous_stop_region_row = srg_sequence_report.iloc[0]

    trips[-1].append(previous_stop_region_row)

    for i, stop_region_row in srg_sequence_report.iterrows():
        if is_there_gap_between(previous_stop_region_row, stop_region_row, gaps):
            trips.append([stop_region_row])
        else:
            trips[-1].append(stop_region_row)

        previous_stop_region_row = stop_region_row

    return trips


def is_there_gap_between(sr1, sr2, gaps):
    if len(gaps[(gaps["start"] >= sr1["sr_end_time"]) & (gaps["stop"] <= sr2["sr_start_time"])]) > 0:
        return True

    return False

def gap_missing_values(report):
    t2 = report.iloc[1:len(report)]["local_time"].astype(float).reset_index(drop=True)
    t1 = report.iloc[0:len(report) - 1]["local_time"].astype(float).reset_index(drop=True)
    gaps = t2 - t1
    gaps.index = report.iloc[1:len(report)]["local_time"]
    head = pd.Series([None], index=[t1.iloc[0].item()])
    return head.append(gaps)