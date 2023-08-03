import json
import os
from datetime import datetime
from pymongo import MongoClient
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()
connection = MongoClient(
    f"""mongodb://{os.environ['MONGO_USERNAME']}:{os.environ['MONGO_PASSWORD']}@mongodb:27017/concept-catalogue?authSource=admin&authMechanism=SCRAM-SHA-1""")
db = connection['concept-catalogue']
errorfileName = args.outputdirectory + "load_errors.json"


def convert_iso(begrep):
    endringstidspunkt = begrep["endringsLogElement"]["endringstidspunkt"]
    gyldigFom = begrep["gyldigFom"]
    gyldigTom = begrep["gyldigTom"]
    if endringstidspunkt is not None:
        begrep["endringsLogElement"]["endringstidspunkt"] = datetime.strptime(endringstidspunkt, "%Y-%m-%dT%H:%M:%S.000Z")
    if gyldigFom is not None:
        begrep["gyldigFom"] = datetime.strptime(gyldigFom, "%Y-%m-%dT%H:%M:%S.000Z")
    if gyldigTom is not None:
        begrep["gyldigTom"] = datetime.strptime(gyldigTom, "%Y-%m-%dT%H:%M:%S.000Z")
    return begrep


with open(args.outputdirectory + 'transformed_concepts.json') as begrep_file:
    transformed_json = json.load(begrep_file)

    total_inserted = 0
    total_failed = 0
    fail_log = {}
    for mongo_id in transformed_json:
        transformed_begrep = convert_iso(transformed_json[mongo_id])
        print("Inserting ID: " + mongo_id)
        insert_result = db.begrep.insert_one(transformed_begrep)
        if insert_result:
            total_inserted += 1
            print("Successfully updated: " + mongo_id)
        else:
            total_failed += 1
            print("Update failed: " + mongo_id)
            fail_log[mongo_id] = transformed_json[mongo_id]
    print("Total number of concepts inserted: " + str(total_inserted))
    print("Total number of concept inserts failed: " + str(total_failed))
    with open(errorfileName, 'w', encoding="utf-8") as err_file:
        json.dump(fail_log, err_file, ensure_ascii=False, indent=4)
