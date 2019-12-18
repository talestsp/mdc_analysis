import os
import pickle
import gc

cache = {}
TOTAL_N_USERS = 163

def save_stop_region_group_object(srg, user_id):
    with open("outputs/stop_region_objects/{}".format(user_id), 'wb') as srg_file:
        pickle.dump(srg, srg_file)

def load_stop_region_group_object(user_id):
    with open("outputs/stop_region_objects/{}".format(user_id), 'rb') as srg_file:
        return pickle.load(srg_file)

def load_all_stop_region_group_object(verbose=True, use_cache=True):
    users_srg = {}
    users = os.listdir("outputs/stop_regions/")

    if "USERS_SRG" in cache.keys() and len(cache["USERS_SRG"]) == TOTAL_N_USERS:
        users_srg = cache["USERS_SRG"]

    else:
        n=0
        for user_id in users:
            n += 1
            if verbose:
                print("Loading user_id: {} - {} out of {}".format(user_id, n, len(users)))
            users_srg[user_id] = load_stop_region_group_object(user_id)

        if use_cache:
            cache["USERS_SRG"] = users_srg

    return users_srg

def load_users_sequence_report(use_cache=True):
    if "USERS_SEQ_REPORT" in cache.keys() and len(cache["USERS_SEQ_REPORT"]) == TOTAL_N_USERS:
        users_seq_report = cache["USERS_SEQ_REPORT"]

    else:
        users_srg = load_all_stop_region_group_object()
        users_seq_report = {}

        for user_id in users_srg.keys():
            users_seq_report[user_id] = users_srg[user_id].sequence_report(enrich_columns=True)

    if use_cache:
        cache["USERS_SEQ_REPORT"] = users_seq_report
    return users_seq_report

def load_users_tags_sequence(sr_stay_time_above_h=0.5):
    users_tags_sequence_original = {}
    users_tags_sequence_filtered = {}

    sizes_original = []
    sizes_filtered = []

    print("Loading Stop Region Group data")
    user_srg = load_all_stop_region_group_object(verbose=False)

    print("Building Stop Region Group sequence")
    for user_id in user_srg.keys():
        seq_report = user_srg[user_id].sequence_report(enrich_columns=True)

        users_tags_sequence_original[user_id] = seq_report["tags"]
        sizes_original.append(len(seq_report))

        if sr_stay_time_above_h:
            seq_report_filtered = seq_report[seq_report["stay_time_h"] > sr_stay_time_above_h]
            users_tags_sequence_filtered[user_id] = seq_report_filtered["tags"]
            sizes_filtered.append(len(seq_report_filtered))

    if sr_stay_time_above_h is None:
        users_tags_sequence_filtered = None

    return {"original": users_tags_sequence_original, "filtered": users_tags_sequence_filtered}