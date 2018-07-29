import json

def credentials_db():
    with open('credentials/credentials_mdc_mysql.json') as f:
        credentials_db_json = json.load(f)

    return credentials_db_json