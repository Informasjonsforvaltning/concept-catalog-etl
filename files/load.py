import json
from pymongo import MongoClient
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()
connection = MongoClient(
    f"""mongodb://{input("Username: ")}:{input("Password: ")}@localhost:27017/concept-catalogue?authSource=admin&authMechanism=SCRAM-SHA-1""")
db = connection["concept-catalogue"]
errorfileName = args.outputdirectory + "load_errors.json"

with open(args.outputdirectory + 'transformed_concepts.json') as begrep_file:
    transformed_json = json.load(begrep_file)

    total_updated = 0
    total_failed = 0
    fail_log = {}
    for mongo_id in transformed_json:
        transformed_data = transformed_json[mongo_id]
        update_result = db.begrep.update_one({'_id': mongo_id}, {'$set': transformed_data})
        if update_result:
            total_updated += 1
        else:
            total_failed += 1
            print("Update failed: " + mongo_id)
            fail_log[mongo_id] = transformed_json[mongo_id]
    print("Total number of concepts updated: " + str(total_updated) + " || Expected: " + str(len(transformed_json)))
    print("Total number of concept updates failed: " + str(total_failed))
    with open(errorfileName, 'w', encoding="utf-8") as err_file:
        json.dump(fail_log, err_file, ensure_ascii=False, indent=4)
