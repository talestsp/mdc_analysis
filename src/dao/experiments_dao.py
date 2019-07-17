import os
import json
TEST_DIR = "outputs/experiments/"

def save_execution_test_data(result_dict, filename):
    create_experiments_dir()
    with open('{}/{}.json'.format(TEST_DIR, filename), 'w') as outfile:
        json.dump(result_dict, outfile)

def load_execution_test_data(filename):
    with open('{}/{}.json'.format(TEST_DIR, filename)) as json_file:
        return json.load(json_file)

def load_execution_test_data_by_model(model):
    model_dir = "{}/{}/".format(TEST_DIR, model)

    executions_data = []
    for filename in os.listdir(model_dir):
        with open("{}/{}".format(model_dir, filename)) as json_file:
            executions_data.append(json.load(json_file))

    return executions_data


def create_experiments_dir():
    try:
        os.mkdir(TEST_DIR)
    except OSError as e:
        pass