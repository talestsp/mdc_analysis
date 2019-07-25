import json
import requests
import time
import pandas as pd
import os
import ast

URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
RAW_DATA_REQUESTS_DIR = '../google-places-poi-grabber/data/raw_data_{}/'
ALL_GOOGLE_PLACES_DATA = {}

def credentials():
    with open('credentials/google_cloud_services.json') as json_file:
        return json.load(json_file)


def nearby_search(latitude, longitude, radius_m):
    response_pages = []
    n_requests = 0

    params = {'location': "{},{}".format(latitude, longitude),
              'key': credentials()["api_key"],
              'radius': "{}".format(radius_m)}

    r = requests.get(url=URL, params=params).json()
    n_requests += 1
    #     print("REQUEST")
    response_pages.append(r)

    while "next_page_token" in r.keys():
        next_page_token = r["next_page_token"]

        r = next_page(next_page_token)
        n_requests += 1
        #         print("REQUEST")

        while r['status'] == "INVALID_REQUEST":
            time.sleep(6)
            r = next_page(next_page_token)
            n_requests += 1
        # print("INVALID, NEW REQUEST")

        response_pages.append(r)

    return response_pages, n_requests


def next_page(next_page_token):
    params = {'key': credentials()["api_key"], "pagetoken": next_page_token}
    r = requests.get(url=URL, params=params).json()
    return r

def group_data_result(data_list):
    all_data_results = []
    for page_data in data_list:
        all_data_results = all_data_results + page_data["results"]
    return all_data_results

def save_data(data, rc, n_requests):
    with open('../google-places-poi-grabber/data/raw_data_{}/results_{}.json'.format(rc.radius_m, rc.id), 'w') as outfile:
        json.dump(data, outfile)

    meta_data = {"rc_id": rc.id, "radius_m": rc.radius_m,
                 "latitude": rc.center_lat, "longitude": rc.center_lon,
                 "data_filename": 'results_{}.json'.format(rc.id),
                 "n_requests": n_requests}
    with open('../google-places-poi-grabber/data/raw_data_{}/metadata_{}.json'.format(rc.radius_m, rc.id), 'w') as outfile:
        json.dump(meta_data, outfile)

def make_request(request_circle):
    data, n_requests = nearby_search(request_circle.center_lat,
                                     request_circle.center_lon,
                                     request_circle.radius_m)

    return data, n_requests

def load_request_circle_data(rc_id, radius_m=75):
    metadata = pd.read_csv('../google-places-poi-grabber/data/raw_data_{}/metadata_{}.json'.format(radius_m, rc_id))
    metadata = metadata[metadata["radius_m"] == radius_m]

    results = pd.DataFrame()

    for filename in metadata["data_filename"].tolist():
        results = results.append(pd.read_csv('../google-places-poi-grabber/data/raw_data_{}/{}'.format(radius_m, filename)))

    return results, metadata

def load_all_request_metadata(radius_m):
    metadatas = []
    for filename in os.listdir(RAW_DATA_REQUESTS_DIR.format(radius_m)):
        if filename.startswith("metadata_"):
            metadatas.append(load_request_metadata(RAW_DATA_REQUESTS_DIR.format(radius_m) + filename))

    return pd.DataFrame(metadatas)

def load_request_metadata(filename):
    with open(filename) as json_file:
        return json.load(json_file)

def load_request_result(filename):
    with open(filename) as json_file:
        return json.load(json_file)

def load_request_result_single_file(radius_m, filename):
    with open(RAW_DATA_REQUESTS_DIR.format(radius_m) + filename) as json_file:
        data_json = json.load(json_file)

    return pd.DataFrame(data_json)

def load_all_google_places_data(radius_m=75, valid_pois=False, round_lat_lon=6, verbose=False):

    if radius_m in ALL_GOOGLE_PLACES_DATA.keys():
        if valid_pois:
            return valid_pois_google(ALL_GOOGLE_PLACES_DATA[radius_m])

        return ALL_GOOGLE_PLACES_DATA[radius_m]

    try:
        results = pd.read_csv('../google-places-poi-grabber/data/pois_data_{}.csv'.format(radius_m))

    except:
        results = pd.DataFrame()

        for filename in os.listdir(RAW_DATA_REQUESTS_DIR.format(radius_m)):
            if filename.startswith("metadata_"):
                metadata = pd.DataFrame([load_request_metadata(RAW_DATA_REQUESTS_DIR.format(radius_m) + filename)])
                if metadata["radius_m"].item() != radius_m:
                    continue

                if verbose:
                    print(metadata["rc_id"].item(), metadata["data_filename"].item())
                result = pd.DataFrame(load_request_result(RAW_DATA_REQUESTS_DIR.format(radius_m) + metadata["data_filename"].item()))

                results = results.append(result)


    results["latitude"] = results["geometry"].apply(lambda geometry: ast.literal_eval(geometry)['location']['lat'])
    results["longitude"] = results["geometry"].apply(lambda geometry: ast.literal_eval(geometry)['location']['lng'])
    results["types"] = results["types"].apply(ast.literal_eval)

    if valid_pois:
        results = valid_pois_google(results)

    results["latitude"] = results["latitude"].apply(lambda value: round(value, round_lat_lon))
    results["longitude"] = results["longitude"].apply(lambda value: round(value, round_lat_lon))

    results = remove_google_places_duplicates(results)
    results = results.set_index("place_id", drop=False)

    cols = results.columns.tolist()
    del cols[cols.index("id")]
    del cols[cols.index("geometry")]
    del cols[cols.index("icon")]
    del cols[cols.index("opening_hours")]
    del cols[cols.index("reference")]
    del cols[cols.index("scope")]

    results = results[cols]

    ALL_GOOGLE_PLACES_DATA[radius_m] = results

    return results

def remove_google_places_duplicates(data):
    del data["photos"]
    data = data.groupby('id', as_index=False).max()
    cols = data.columns.tolist()
    del cols[cols.index("types")]
    return data.drop_duplicates(subset=cols)

def valid_pois_google(google_places_data):
    return google_places_data[~(
                (google_places_data["types"].apply(len) == 2) &
                (google_places_data["types"].apply(lambda list : "point_of_interest" in list)) &
                (google_places_data["types"].apply(lambda list : "establishment" in list)) )]


def useful_types(types):
    if "establishment" in types:
        del [types[types.index("establishment")]]

    if "point_of_interest" in types:
        del [types[types.index("point_of_interest")]]

    return types


