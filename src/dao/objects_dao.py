import os
import pickle

def save_stop_region_group_object(srg, user_id):
    with open("outputs/stop_region_objects/{}".format(user_id), 'wb') as srg_file:
        pickle.dump(srg, srg_file)

def load_stop_region_group_object(user_id):
    with open("outputs/stop_region_objects/{}".format(user_id), 'rb') as srg_file:
        return pickle.load(srg_file)

def load_all_stop_region_group_object():
    users_srg = {}
    users = os.listdir("outputs/stop_regions/")

    n=0
    for user_id in users:
        n += 1
        print("Loading user_id: {} - {} out of {}".format(user_id, n, len(users)))
        users_srg[user_id] = load_stop_region_group_object(user_id)

    return users_srg
