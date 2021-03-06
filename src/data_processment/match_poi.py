import os
from src.dao import csv_dao
from src.poi_grabber import google_places
from src.utils import geo
from src.utils import others


def knn_by_clusters(centroids, pois, k_neighbors, k_partitions=4):
    centroids["cluster"] = others.partitions_k_means(centroids, k_partitions=k_partitions, columns=["latitude", "longitude"])

    user_knn_pois = []

    for partition in centroids["cluster"].drop_duplicates():
        print("--")
        print("Partition: {}".format(partition))
        partition_centroids = centroids[centroids["cluster"] == partition]
        print("Stop Regions in this parittion: {}".format(len(partition_centroids)))

        pois["latitude"] = pois["lat_4326"]
        pois["longitude"] = pois["lon_4326"]

        close_pois = geo.grab_pois_by_stop_region_bounding_box_expand_fixed(pois, partition_centroids,
                                                                            expand_value=0.004)

        if len(close_pois) == 0:
            continue

        user_knn_pois = user_knn_pois + geo.knn_pois(partition_centroids, close_pois, k=k_neighbors)

    return user_knn_pois


def knn_by_clusters_google_places(centroids, pois, k_neighbors, k_partitions=4):
    centroids["cluster"] = others.partitions_k_means(centroids, k_partitions=k_partitions, columns=["latitude", "longitude"])

    user_knn_pois = []

    for partition in centroids["cluster"].drop_duplicates():
        print("--")
        print("Partition: {}".format(partition))
        partition_centroids = centroids[centroids["cluster"] == partition]
        print("Stop Regions in this parittion: {}".format(len(partition_centroids)))

        pois["latitude"] = pois["lat_4326"]
        pois["longitude"] = pois["lon_4326"]

        close_pois = geo.grab_pois_by_stop_region_bounding_box_expand_fixed(pois, partition_centroids,
                                                                            expand_value=0.004)

        if len(close_pois) == 0:
            continue

        user_knn_pois = user_knn_pois + geo.knn_pois_google_places(partition_centroids, close_pois, k=k_neighbors)

    return user_knn_pois


def match_poi(valid_pois, users=csv_dao.list_stop_region_usernames(), k_neighbors=30, k_partitions=6):

    for user in users:
        print("\n\n")
        print("**********")
        print("User:", user)

        sr_centroids = csv_dao.load_user_stop_regions_centroids(user)

        print("Stop Regions:", len(sr_centroids))
        print("-----")

        user_dir = os.getcwd() + "/outputs/hot_osm_sr_knn/" + str(user)
        try:
            os.mkdir(user_dir)
        except FileExistsError:
            print("User already computed... skipping")
            continue
            # shutil.rmtree(user_dir)
            # os.mkdir(user_dir)
        except FileNotFoundError:
            os.mkdir(user_dir)

        print("Computing")

        if len(sr_centroids) < k_partitions:
            user_knn_pois = knn_by_clusters(sr_centroids, valid_pois, k_neighbors, k_partitions=1)

        else:
            user_knn_pois = knn_by_clusters(sr_centroids, valid_pois, k_neighbors, k_partitions=k_partitions)

        for knn in user_knn_pois:
            sr_id = knn["sr_id"].drop_duplicates().item()
            knn.to_csv(user_dir + "/" + "/" + "sr_" + sr_id + "_knn" + ".csv", index=False)


def match_poi_google_places(valid_pois, users=csv_dao.list_stop_region_usernames(), k_neighbors=30, k_partitions=6):

    for user in users:
        print("\n\n")
        print("**********")
        print("User:", user)

        sr_centroids = csv_dao.load_user_stop_regions_centroids(user)

        print("Stop Regions:", len(sr_centroids))
        print("-----")

        user_dir = os.getcwd() + "/outputs/google_places_sr_knn/" + str(user)
        try:
            os.mkdir(user_dir)
        except FileExistsError:
            print("User already computed... skipping")
            continue
            # shutil.rmtree(user_dir)
            # os.mkdir(user_dir)
        except FileNotFoundError:
            os.mkdir(user_dir)

        print("Computing")

        if len(sr_centroids) < k_partitions:
            user_knn_pois = knn_by_clusters_google_places(sr_centroids, valid_pois, k_neighbors, k_partitions=1)

        else:
            user_knn_pois = knn_by_clusters_google_places(sr_centroids, valid_pois, k_neighbors, k_partitions=k_partitions)

        for knn in user_knn_pois:
            sr_id = knn["sr_id"].drop_duplicates().item()
            knn.to_csv(user_dir + "/" + "/" + "sr_" + sr_id + "_knn" + ".csv", index=False)


if __name__ == "__main__":
    valid_pois = google_places.load_all_google_places_data(valid_pois=True)

    valid_pois["lat_4326"] = valid_pois["latitude"]
    valid_pois["lon_4326"] = valid_pois["longitude"]

    users = csv_dao.list_stop_region_usernames()
    match_poi_google_places(valid_pois, users=users)
