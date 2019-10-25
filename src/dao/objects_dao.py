import pickle

def save_stop_region_group_object(srg, user_id):
    with open("outputs/stop_region_objects/{}".format(user_id), 'wb') as srg_file:
        pickle.dump(srg, srg_file)

def load_stop_region_group_object(user_id):
    with open("outputs/stop_region_objects/{}".format(user_id), 'rb') as srg_file:
        return pickle.load(srg_file)
