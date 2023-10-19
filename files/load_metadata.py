# last opp transformed metadata, og slett alle med _id = data.brreg

import json
import os
from pymongo import MongoClient
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()
connection = MongoClient(
    f"""mongodb://{os.environ['MONGO_USERNAME']}:{os.environ['MONGO_PASSWORD']}@mongodb:27017/conceptHarvester?authSource=admin&authMechanism=SCRAM-SHA-1""")
db = connection.conceptHarvester
errorfileName = args.outputdirectory + "load_metadata_errors.json"


with open(args.outputdirectory + 'transformed_metadata.json') as metadata_file:
    transformed_json = json.load(metadata_file)

    total_inserted = 0
    total_failed = 0
    fail_log = {}
    for mongo_id in transformed_json:
        transformed_begrep = transformed_json[mongo_id]
        insert_result = db.conceptMeta.update_one({'_id': mongo_id}, {"$set": transformed_begrep})
        if insert_result.modified_count == 1:
            total_inserted += 1
        else:
            total_failed += 1
            print("Update failed: " + mongo_id)
            fail_log[mongo_id] = transformed_json[mongo_id]
    print("Total number of concepts inserted: " + str(total_inserted))
    print("Total number of concept inserts failed: " + str(total_failed))
    with open(errorfileName, 'w', encoding="utf-8") as err_file:
        json.dump(fail_log, err_file, ensure_ascii=False, indent=4)

if input("Do you want to delete the metadata for brreg concepts from conceptHarvester (y/n) ?") in ["y", "yes", "yep", "roger", "jada", "ja", "j", "yeah", "can confirm", "yessir", "yessiree"]:
    delete_result = db.conceptMeta.delete_many({"_id": {'$regex': "http://data.brreg.no/begrep/", '$options': 'i'}})
    if delete_result:
        print("Successfully deleted metadata for brreg concepts" + str(delete_result.deleted_count))
    else:
        exit("Delete failed, exiting ... | Delete count: " + str(delete_result.deleted_count))
else:
    exit("Exiting ...")
