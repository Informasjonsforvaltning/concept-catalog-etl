import json
import os
from datetime import datetime
from pymongo import MongoClient
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()
connection = MongoClient(
    f"""mongodb://{os.environ['MONGO_USERNAME']}:{os.environ['MONGO_PASSWORD']}@mongodb:27017/catalog-history-service?authSource=admin&authMechanism=SCRAM-SHA-1""")
db = connection['catalog-history-service']
errorfileName = args.outputdirectory + "load_history_errors.json"


def convert_iso(story):
    createdDate = story["datetime"]
    if createdDate is not None:
        story["datetime"] = datetime.strptime(createdDate, "%Y-%m-%dT%H:%M:%S.000Z")
    return story


with open(args.outputdirectory + 'transformed_history.json') as history_file:
    transformed_json = json.load(history_file)

    total_inserted = 0
    total_failed = 0
    fail_log = {}
    for mongo_id in transformed_json:
        # print("Inserting history for concept: " + mongo_id)
        for history in transformed_json[mongo_id]:
            transformed_history = convert_iso(history)
            # print("Inserting ID: " + transformed_history["_id"])
            insert_result = db.updates.insert_one(transformed_history)
            if insert_result:
                total_inserted += 1
                # print("Successfully updated: " + mongo_id)
            else:
                total_failed += 1
                print("Update failed: " + mongo_id)
                fail_log[mongo_id] = transformed_json[mongo_id]
    print("Total number of histories inserted: " + str(total_inserted))
    print("Total number of history inserts failed: " + str(total_failed))
    with open(errorfileName, 'w', encoding="utf-8") as err_file:
        json.dump(fail_log, err_file, ensure_ascii=False, indent=4)
