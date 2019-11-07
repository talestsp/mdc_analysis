#Early birds, night owls, and tireless/recurring itinerants:
# An exploratory analysis of extreme transit behaviors in Beijing, China

#https://www.sciencedirect.com/science/article/pii/S0197397516301539

import pandas as pd

def early_bird(user_srg, leaving_time=6):
    '''
    It considers times before leaving_time inclusive
    :param user_srg:
    :param leaving_time:
    :return:
    '''
    user_data = sequence_report(user_srg)
    f = first_trip_of_the_day(user_data)
    f = filter_weekdays(f, "start_weekday")
    f = filter_before_hour(f, "start_time", leaving_time)

    n_week_days = len(filter_weekdays(df=user_data, weekday_colname="start_weekday"))

    return len(f) / float(n_week_days)


def nigh_owl(user_srg, boarding_time=20):
    '''
    It considers times after boarding_time inclusive
    :param user_srg:
    :param boarding_time:
    :return:
    '''
    user_data = sequence_report(user_srg)
    l = last_trip_of_the_day(user_data)
    l = filter_weekdays(l, "start_weekday").head()
    l = filter_after_hour(l, "end_time", boarding_time)

    n_week_days = len(filter_weekdays(df=user_data, weekday_colname="start_weekday"))

    return len(l) / float(n_week_days)

def tireless_intinerant(user_srg, commuting_time_m=60, threshold_max_time_m=180):
    user_data = sequence_report(user_srg)
    data_week = filter_weekdays(user_data, "start_weekday")

    hw = data_week["tags"].apply(lambda lista: "HOME" in lista or "WORK" in lista)
    data_week_clean = data_week[hw]

    time_diffs = time_diff_between_diff_tags(data_week_clean)

    if len(time_diffs) == 0:
        return 0

    time_diffs_clean = time_diffs[time_diffs["time_diff_s"] <= (threshold_max_time_m * 60)]

    ti_rates = time_diffs_clean[time_diffs_clean["time_diff_s"] >= (commuting_time_m * 60)]

    return len(ti_rates) / len(time_diffs_clean)

def time_diff_between_diff_tags(report):
    rows = []

    counter = 0

    while counter < (len(report) - 2):
        from_sr_id = report.index[counter]
        counter += 1
        to_sr_id_candidate = report.index[counter]

        while report.loc[from_sr_id]["tags"] == report.loc[to_sr_id_candidate]["tags"] and counter < (len(report) - 1):
            counter += 1
            to_sr_id_candidate = report.index[counter]

        if report.loc[from_sr_id]["tags"] != report.loc[to_sr_id_candidate]["tags"]:
            time_diff = report.loc[to_sr_id_candidate]["sr_start_time"] - report.loc[from_sr_id]["sr_end_time"]

            rows.append({"from_sr_id": from_sr_id,
                         "to_sr_id": to_sr_id_candidate,
                         "from_tags": report.loc[from_sr_id]["tags"],
                         "to_tags": report.loc[to_sr_id_candidate]["tags"],
                         "time_diff_s": time_diff,
                         "time_diff_h": time_diff / 3600})

        #skipping consecutive equals
        while counter < (len(report) - 2) and report.loc[to_sr_id_candidate]["tags"] == report.loc[report.index[counter + 1]]["tags"]:
            counter += 1

    if len(rows) == 0:
        return pd.DataFrame(rows)

    return pd.DataFrame(rows)[["from_sr_id", "to_sr_id", "from_tags", "to_tags", "time_diff_s", "time_diff_h"]]

def first_trip_of_the_day(report):
    report = report.sort_values("sr_start_time")
    return report.reset_index().groupby("start_date").apply(lambda gr: gr.iloc[0])[
        ["sr", "start_weekday", "start_time"]].reset_index().set_index("sr")


def last_trip_of_the_day(report):
    report = report.sort_values("sr_start_time")
    return report.reset_index().groupby("start_date").apply(lambda gr: gr.iloc[-1])[
        ["sr", "start_weekday", "end_time"]].reset_index().set_index("sr")


def filter_weekdays(df, weekday_colname):
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    return df[df[weekday_colname].isin(weekdays)]


def filter_before_hour(df, time_col, time_threshold):
    return df[df[time_col].apply(time_str_hour) <= time_threshold]


def filter_after_hour(df, time_col, time_threshold):
    return df[df[time_col].apply(time_str_hour) >= time_threshold]


def time_str_hour(time_str):
    return int(time_str.split(":")[0])

def sequence_report(srg):
    seq = srg.sequence_report(enrich_columns=True)
    seq = seq[["sr", "sr_start_time", "sr_end_time", "last_tags", "tags", "stay_time_h", "start_weekday", "start_date", "start_time", "end_date", "end_time", "end_weekday"]]
    seq = seq.set_index("sr")
    return seq.sort_values("sr_start_time")