def jaccard(list_a, list_b):
    try:
        jaccard_metric = len(set(list_a).intersection(set(list_b))) / len(set(list_a).union(set(list_b)))
    except ZeroDivisionError:
        jaccard_metric = 0

    return jaccard_metric