import json
import os
from pymongo import MongoClient
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()
connection = MongoClient(
    f"""mongodb://{os.environ['MONGO_USERNAME']}:{os.environ['MONGO_PASSWORD']}@mongodb:27017/comments?authSource=admin&authMechanism=SCRAM-SHA-1""")
db = connection['comments']
errorfileName = args.outputdirectory + "load_comment_users_errors.json"


with open(args.outputdirectory + 'transformed_users.json') as user_file:
    transformed_json = json.load(user_file)

    total_inserted = 0
    total_failed = 0
    fail_log = {}
    for mongo_id in transformed_json:
        print("Inserting ID: " + mongo_id)
        insert_result = db.user.insert_one(transformed_json[mongo_id])
        if insert_result:
            total_inserted += 1
            print("Successfully updated: " + mongo_id)
        else:
            total_failed += 1
            print("Update failed: " + mongo_id)
            fail_log[mongo_id] = transformed_json[mongo_id]
    print("Total number of users inserted: " + str(total_inserted))
    print("Total number of user inserts failed: " + str(total_failed))
    with open(errorfileName, 'w', encoding="utf-8") as err_file:
        json.dump(fail_log, err_file, ensure_ascii=False, indent=4)
