import json

from sklearn.cluster import KMeans

def credentials_db():
    with open('src/credentials/credentials_mdc_mysql.json') as f:
        credentials_db_json = json.load(f)

    return credentials_db_json

def partitions(points, k_partitions, columns):
    kmeans = KMeans(n_clusters=k_partitions, random_state=0).fit(points[columns])
    return kmeans.labels_
