import json
import os

FOURSQUARE_POI_DIR = "/home/tales/dev/poi_grabber/out/poi/foursquare/"
GOOGLE_PLACES_POI_DIR = "/home/tales/dev/poi_grabber/out/poi/google_places/"

def load_pois(dir):
    pois = []
    poi_files = os.listdir(dir)

    for poi_file in poi_files:
        if not poi_file.endswith(".json"):
            continue

        with open(dir + poi_file) as f:
            pois.append(json.load(f))

    return pois

def load_google_pois():
    return load_pois(GOOGLE_PLACES_POI_DIR)

def load_foursquare_pois():
    return load_pois(FOURSQUARE_POI_DIR)



