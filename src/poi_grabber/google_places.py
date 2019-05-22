import json
import requests
import sys

URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"


def credentials():
    with open('credentials/credentials.json') as json_file:
        return json.load(json_file)


def nearby_search(latitude, longitude, radius_m):
    response_pages = []

    PARAMS = {'location': "{},{}".format(latitude, longitude), 'key': credentials()["api_key"],
              'radius': "{}".format(radius_m)}
    r = requests.get(url=URL, params=PARAMS).json()
    response_pages.append(r)

    while "next_page_token" in r.keys():
        next_page_token = r["next_page_token"]

        r = next_page(next_page_token)

        while r['status'] == "INVALID_REQUEST":
            r = next_page(next_page_token)

        response_pages.append(r)

    return response_pages


def next_page(next_page_token):
    PARAMS = {'key': credentials()["api_key"], "pagetoken": next_page_token}
    r = requests.get(url=URL, params=PARAMS).json()
    return r