import pandas as pd
from src.utils import geo
from src.dao import csv_dao
from src.poi_grabber import google_places
from src.plot import plot2
from src.data_processment.stop_region_agglutination import agglutinate, agglutinate_consecutive_stop_regions, same_closest_poi

class StopRegion:
    '''
          Use EPSG 4326
    '''
    def __init__(self, centroid_lat, centroid_lon, start_time, end_time, user_id, sr_id, semantics=[], agglutination=[]):
        self.centroid_lat = round(centroid_lat, 5)
        self.centroid_lon = round(centroid_lon, 5)
        self.start_time = start_time
        self.end_time = end_time
        self.sr_id = sr_id

        self.user_id = user_id
        self.close_pois = pd.DataFrame()
        self.close_pois_ids = []
        self.semantics = semantics
        self.agglutination = agglutination

        self.close_pois = None

    def agglutinate_with(self, another_stop_regions):
        agglutination_params = agglutinate([self] + another_stop_regions)
        return StopRegion(**agglutination_params)

    def is_agglutination(self):
        return len(self.agglutination) > 0

    def distance_to_point(self, point, lat_col="latitude", lon_col="longitude"):
        return geo.distance_epsg_4326(self.centroid_lat, self.centroid_lon,
                                      point[lat_col], point[lon_col])

    def distance_to_another_sr(self, another_sr):
        return geo.distance_epsg_4326(self.centroid_lat, self.centroid_lon,
                                      another_sr.centroid_lat, another_sr.centroid_lon)

    def delta_time_to_another_sr(self, another_sr):
        return min(abs(self.start_time - another_sr.end_time), abs(self.end_time - another_sr.start_time))

    def __merge_agg_pois(self):
        close_pois_agg = pd.DataFrame()

        for sr in self.agglutination:
            close_pois_agg = close_pois_agg.append(sr.close_pois)

        distances = close_pois_agg.groupby("place_id")["distance"].mean().to_frame()
        del close_pois_agg["distance"]
        close_pois_agg = close_pois_agg.drop_duplicates(subset="place_id")

        return close_pois_agg.set_index("place_id").merge(distances, left_index=True, right_index=True)

    def load_close_pois(self, verbose=False):
        if verbose:
            print("Loading POIs")

        if self.is_agglutination():
            self.close_pois = self.__merge_agg_pois()
            return self.close_pois

        pois = csv_dao.load_knn_pois_by_stop_region(self)[["distance", "place_id", "position"]]
        self.close_pois = google_places.load_all_google_places_data(valid_pois=True).merge(pois, on="place_id", how="inner").sort_values(by="distance")

        if verbose:
            print("{} POIs loaded".format(len(self.close_pois)))
        return self.close_pois

    def __remove_tags_from_list(self, tags_list, tags_to_be_removed):
        use_pois_tags = []
        for poi_types in tags_list:
            for to_be_removed in tags_to_be_removed:
                if to_be_removed in poi_types:
                    del poi_types[poi_types.index(to_be_removed)]
            use_pois_tags.append(poi_types)

        return use_pois_tags

    def tag_closest_poi(self, remove_tags=["establishment", "point_of_interest"]):
        pois_tags = self.closest_poi()["types"]
        return self.__remove_tags_from_list(pois_tags.tolist(), remove_tags)

    def closest_poi(self):
        if self.close_pois is None:
            self.load_close_pois()
        return self.close_pois[self.close_pois["distance"] == self.close_pois["distance"].min()]

    def tag_radius_pois(self, radius, remove_tags=["establishment", "point_of_interest"]):
        pois_tags = self.radius_pois(radius)["types"]
        return self.__remove_tags_from_list(pois_tags.tolist(), remove_tags)

    def radius_pois(self, radius):
        if self.close_pois is None:
            self.load_close_pois()
        return self.close_pois[self.close_pois["distance"] <= radius]

    def centroid_mercator(self):
        geo.gps_loc_to_web_mercator(self.centroid_lat, self.centroid_lon)

    def plot(self, p=None):
        return plot2.plot_stop_region(self, p=p)

class StopRegionSequence:
    '''
          Use EPSG 4326
    '''
    def __init__(self, stop_region_sequence):
            self.stop_region_sequence = stop_region_sequence

    def plot(self, title="", width=800, height=600, fill_color="magenta", p=None):
        return plot2.plot_stop_region_sequence(stop_region_sequence=self, title=title,
                                               width=width, height=height, fill_color=fill_color, p=p)

    def sequence_report(self):
        sequence_report = []

        last_sr = self.stop_region_sequence[0]

        for sr in self.stop_region_sequence[1:]:
            sequence_row = {"distance": round(sr.distance_to_another_sr(last_sr), 1),
                            "delta_t": sr.delta_time_to_another_sr(last_sr),
                            "last_sr": last_sr.sr_id, "last_sr_tag": last_sr.tag_closest_poi(),
                            "sr": sr.sr_id, "sr_tag": sr.tag_closest_poi(),
                            "last_sr_semantics": last_sr.semantics,
                            "sr_semantics": sr.semantics}
            sequence_report.append(sequence_row)
            last_sr = sr

        cols = ["delta_t", "distance", "last_sr_tag", "sr_tag", "last_sr_semantics", "sr_semantics", "last_sr", "sr"]
        return pd.DataFrame(sequence_report)[cols]

    def agglutinate_stop_regions(self):
        agglutinated = []
        singles = []

        agglutinated_srs = agglutinate_consecutive_stop_regions(self.stop_region_sequence, same_closest_poi)

        for group in agglutinated_srs:
            if len(group) == 1:
                singles.append(group[0])
            else:
                agg_sr = agglutinate(group)
                agglutinated.append(StopRegion(**agg_sr))

        return StopRegionSequence((agglutinated + singles).sort(key=lambda x: x.start_time, reverse=False))


def sr_row_to_stop_region(sr_row):
    if sr_row["tag"] is None:
        semantics = []
    elif len(sr_row["tag"].split(",")) == 1 and sr_row["tag"].split(",")[0] == "":
        semantics = []
    else:
        semantics = sr_row["tag"].split(",")

    return StopRegion(centroid_lat = sr_row["latitude"], centroid_lon=sr_row["longitude"],
                      start_time=sr_row["local_start_time"], end_time=sr_row["local_end_time"],
                      user_id=sr_row["user_id"], sr_id=sr_row["sr_id"], semantics=semantics)

if __name__ == "__main__":
    sr = StopRegion(46.7, 6.8, "1234_56")
    print(sr.centroid_mercator())

