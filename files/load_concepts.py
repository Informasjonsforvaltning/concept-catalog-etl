import json
import os
from pymongo import MongoClient
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()
connection = MongoClient(
    f"""mongodb://{os.environ['MONGO_USERNAME']}:{os.environ['MONGO_PASSWORD']}@mongodb:27017/datasetCatalog?authSource=admin&authMechanism=SCRAM-SHA-1""")
db = connection.datasetCatalog

with open(args.outputdirectory + 'transformed_datasets.json') as catalogs_file:
    transformed_json = json.load(catalogs_file)

    total_updated = 0
    total_failed = 0
    fail_log = {}
    for mongo_id in transformed_json:
        to_be_updated = transformed_json[mongo_id]
        print("Updating ID: " + mongo_id)
        insert_result = db.datasets.find_one_and_update({'_id': mongo_id},  {'$set': to_be_updated})
        if insert_result:
            total_updated += 1
            print("Successfully updated: " + mongo_id)
        else:
            total_failed += 1
            print("Update failed: " + mongo_id)
            fail_log[mongo_id] = transformed_json[mongo_id]
        total_updated += 1
    print("Total number of datasets updated: " + str(total_updated))
    print("Total number of datasets updates failed: " + str(total_failed))
    with open("load_errors.json", 'w', encoding="utf-8") as err_file:
        json.dump(fail_log, err_file, ensure_ascii=False, indent=4)
