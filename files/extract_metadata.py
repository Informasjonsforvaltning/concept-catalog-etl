import json
import os
from pymongo import MongoClient
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()
connection = MongoClient(
    f"""mongodb://{os.environ['MONGO_USERNAME']}:{os.environ['MONGO_PASSWORD']}@mongodb:27017/conceptHarvester?authSource=admin&authMechanism=SCRAM-SHA-1""")
admin_connection = MongoClient(
    f"""mongodb://{os.environ['MONGO_USERNAME']}:{os.environ['MONGO_PASSWORD']}@mongodb:27017/fdk-harvest-admin?authSource=admin&authMechanism=SCRAM-SHA-1""")
admin_db = connection['fdk-harvest-admin']

response = input("Running this script will delete the harvest endpoint for brreg concepts from fdk-harvest-admin, do you want to continue (y/n) ?")
if response not in ["y", "yes", "yep", "roger", "jada", "ja", "j", "yeah", "can confirm", "yessir", "yessiree"]:
    exit("Exiting ...")

delete_result = admin_db.datasources.delete_one({"url": "https://data.brreg.no/begrep/"})
if delete_result:
    print("Successfully deleted datasource for https://data.brreg.no/begrep/")
else:
    exit("Delete failed, exiting ...")

db = connection.conceptHarvester
fdk_pattern = re.compile(os.environ['CONCEPT_CATALOG_URI'], re.I)
brreg_pattern = re.compile("http://data.brreg.no/begrep/", re.I)
fdk_concept_list = list(db.conceptMeta.find({"_id": {'$regex': fdk_pattern}}))
brreg_concept_list = list(db.conceptMeta.find({"_id": {'$regex': brreg_pattern}}))
brregMetas = {}
fdkMetas = {}
for id_dict in brreg_concept_list:
    _id = id_dict["_id"]
    brregMetas[_id] = {}
    brregMetas[_id]["fdkId"] = id_dict.get("fdkId")
    brregMetas[_id]["issued"] = id_dict.get("issued")
for id_dict in fdk_concept_list:
    _id = id_dict["_id"]
    fdkMetas[_id] = {}
    fdkMetas[_id]["fdkId"] = id_dict.get("fdkId")
    fdkMetas[_id]["issued"] = id_dict.get("issued")

print("Total number of extracted brregMetas: " + str(len(brregMetas)))
print("Total number of extracted fdkMetas: " + str(len(brregMetas)))

with open(args.outputdirectory + 'mongo_conceptMeta.json', 'w', encoding="utf-8") as outfile:
    json.dump([brregMetas, fdkMetas], outfile, ensure_ascii=False, indent=4)
