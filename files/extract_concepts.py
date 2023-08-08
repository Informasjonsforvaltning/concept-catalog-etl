import json
import os
from pymongo import MongoClient
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()
connection = MongoClient(
    f"""mongodb://{os.environ['MONGO_USERNAME']}:{os.environ['MONGO_PASSWORD']}@mongodb:27017/concept-catalogue?authSource=admin&authMechanism=SCRAM-SHA-1""")

db = connection['concept-catalogue']

concept_list = list(db.begrep.find())
concepts = {}
for id_dict in concept_list:
    _id = id_dict["_id"]
    concepts[_id] = {}
    concepts[_id]["merknad"] = id_dict.get("merknad")
    concepts[_id]["eksempel"] = id_dict.get("eksempel")
print("Total number of extracted concepts: " + str(len(concepts)))

with open(args.outputdirectory + 'mongo_concepts.json', 'w', encoding="utf-8") as outfile:
    json.dump(concepts, outfile, ensure_ascii=False, indent=4)
