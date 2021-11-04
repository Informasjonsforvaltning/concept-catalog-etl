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

#TODO: Resten av ETL'en. Mål: oppdatere gamle urler i seOgså-listene

concept_list = list(db.conceptMeta.find())
conceptMetas = {}
for id_dict in concept_list:
    _id = id_dict["_id"]
    conceptMetas[_id] = {}
    conceptMetas[_id]["fdkId"] = _id.get("fdkId")
    conceptMetas[_id]["isPartOf"] = _id.get("isPartOf")
    conceptMetas[_id]["issued"] = _id.get("issued")
    conceptMetas[_id]["modified"] = _id.get("modified")
    conceptMetas[_id]["_class"] = _id.get("_class")
print("Total number of extracted conceptMetas: " + str(len(conceptMetas)))

with open(args.outputdirectory + 'mongo_conceptMeta.json', 'w', encoding="utf-8") as outfile:
    json.dump(conceptMetas, outfile, ensure_ascii=False, indent=4)

collection_list = list(db.collectionMeta.find())
collectionMetas = {}
for id_dict in collection_list:
    _id = id_dict["_id"]
    collectionMetas[_id] = {}
    collectionMetas[_id]["fdkId"] = _id.get("fdkId")
    collectionMetas[_id]["concepts"] = _id.get("concepts")
    collectionMetas[_id]["issued"] = _id.get("issued")
    collectionMetas[_id]["modified"] = _id.get("modified")
    collectionMetas[_id]["_class"] = _id.get("_class")
print("Total number of extracted collectionMetas: " + str(len(collectionMetas)))

with open(args.outputdirectory + 'mongo_collectiontMeta.json', 'w', encoding="utf-8") as outfile:
    json.dump(collectionMetas, outfile, ensure_ascii=False, indent=4)
