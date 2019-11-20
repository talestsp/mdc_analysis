import pandas as pd
import numpy as np
import os
import json
import math
import copy
import gc

from src.exceptions.exceptions import EmptyDirectory


TEST_DIR = "outputs/experiments/"

def save_execution_test_data(result_dict, filename):
    create_experiments_dir()
    with open('{}/{}.json'.format(TEST_DIR, filename), 'w') as outfile:
        json.dump(result_dict, outfile)

def execution_file_exists(filename, model):
    return filename in os.listdir(TEST_DIR + "/" + model)

def load_execution_test_data(filename):
    with open('{}/{}.json'.format(TEST_DIR, filename)) as json_file:
        return json.load(json_file)

def load_execution_test_data(dir):
    dir_path = "{}/{}/".format(TEST_DIR, dir)

    if len(os.listdir(dir_path)) == 0:
        raise EmptyDirectory(dir_path)

    executions_data = []
    for filename in os.listdir(dir_path):
        with open("{}/{}".format(dir_path, filename)) as json_file:
            executions_data.append(json.load(json_file))

    return executions_data


def create_experiments_dir():
    try:
        os.mkdir(TEST_DIR)
    except OSError as e:
        pass

def round_up_list(num_list):
    rounded = [math.ceil(i) for i in num_list]
    return rounded

def hits_contain(df):
    df = copy.deepcopy(df)
    df["hits_contain"] = df["partial_hits"].apply(lambda lista : round_up_list(lista))
    df["hits_contain_mean"] = df["partial_hits"].apply(lambda lista : pd.Series(round_up_list(lista)).mean())
    return df

def json_to_dataframe(json_list, simple_cols=True):
    df = pd.DataFrame(json_list)

    df["iteration"] = df["iteration"].astype(str)
    df["k"] = df["k"].astype(str)

    df["acc"] = df["total_hits"] / df["test_size"]

    try:
        df["partial_hits_mean"] = df["partial_hits"].apply(lambda lista: pd.Series(lista).mean())
    except KeyError:
        df["partial_hits_mean"] = [np.NaN] * len(df)

    gc.collect()

    if simple_cols:
        del df["states_not_trained_as_origin"]
        del df["hits"]
        del df["misses"]

    return df