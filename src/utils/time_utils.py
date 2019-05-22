import datetime
import calendar

DAY_SECONDS = 86400

def enrich_time_columns(gps_data, time_col="local_time"):
    gps_data["hour"] = [datetime.datetime.utcfromtimestamp(gps_time).hour for gps_time in gps_data[time_col]]
    gps_data["min"] = [datetime.datetime.utcfromtimestamp(gps_time).minute for gps_time in gps_data[time_col]]
    gps_data["sec"] = [datetime.datetime.utcfromtimestamp(gps_time).second for gps_time in gps_data[time_col]]
    gps_data["weekday"] = [calendar.day_name[datetime.datetime.utcfromtimestamp(gps_time).weekday()] for gps_time in
                           gps_data[time_col]]
    gps_data["local_datetime"] = [datetime.datetime.utcfromtimestamp(gps_time).strftime('%Y-%m-%d %H:%M:%S') for gps_time in
                                  gps_data[time_col]]

    return gps_data


def local_time(data, time_col="time", tz_col="tz"):
    data["local_" + time_col] = data[time_col] + data[tz_col]
    return data

def diff_between_dates(timestamp0, timestamp1):
    d0 = datetime.datetime.fromtimestamp(timestamp0)
    d1 = datetime.datetime.fromtimestamp(timestamp1)
    delta_days = (d1 - d0).days + ((d1 - d0).seconds / (DAY_SECONDS))
    return delta_days
