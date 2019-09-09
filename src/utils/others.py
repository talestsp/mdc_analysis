import json

from sklearn.cluster import KMeans
from src.exceptions import exceptions

def credentials_db():
    with open('src/credentials/credentials_mdc_mysql.json') as f:
        credentials_db_json = json.load(f)

    return credentials_db_json

def partitions_k_means(points, k_partitions, columns):
    kmeans = KMeans(n_clusters=k_partitions, random_state=0).fit(points[columns])
    return kmeans.labels_

def partitions_list(list, k):
    if len(list) < k:
        raise exceptions.TagsLengthNeedsToBeGreaterThanK()

    partition_size = int(len(list) / k)

    partitions = []
    for i in range(k):
        partitions.append(list[i * partition_size: (i + 1) * partition_size])

    if k * partition_size < len(list):
        partitions[-1] = partitions[-1] + list[k * partition_size: len(list)]

    return partitions

def k_fold_iteration(lista, k):
    partitions = partitions_list(lista, k)

    k_fold_iteration_list = []

    for i in range(len(partitions)):
        train_indexes = list(range(len(partitions)))
        train_indexes.remove(i)

        train = []
        for train_index in train_indexes:
            train = train + partitions[train_index]

        k_fold_iteration_list.append({"test": partitions[i], "train": train})

    return k_fold_iteration_list


def concat_lists(lists):
    concat = []
    for lista in lists:
        concat = concat + lista
    return concat


def remove_list_elements(list, elements):
    for el in elements:
        if el in list:
            list.remove(el)
    return list
