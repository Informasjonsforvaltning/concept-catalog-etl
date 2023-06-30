import json
import os
from pymongo import MongoClient
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()
connection = MongoClient(
    f"""mongodb://{os.environ['MONGO_USERNAME']}:{os.environ['MONGO_PASSWORD']}@mongodb:27017/concept-catalogue?authSource=admin&authMechanism=SCRAM-SHA-1""")
db = connection.begrep

with open(args.outputdirectory + 'transformed_concepts.json') as begrep_file:
    transformed_json = json.load(begrep_file)

    total_updated = 0
    total_failed = 0
    fail_log = {}
    for mongo_id in transformed_json:
        transformed_begrep = transformed_json[mongo_id]
        print("Inserting ID: " + mongo_id)
        insert_result = db.begrep.insert_one(transformed_begrep)
        if insert_result:
            total_updated += 1
            print("Successfully updated: " + mongo_id)
        else:
            total_failed += 1
            print("Update failed: " + mongo_id)
            fail_log[mongo_id] = transformed_json[mongo_id]
        total_updated += 1
    print("Total number of concepts inserted: " + str(total_updated))
    print("Total number of concept inserts failed: " + str(total_failed))
    with open("load_errors.json", 'w', encoding="utf-8") as err_file:
        json.dump(fail_log, err_file, ensure_ascii=False, indent=4)
