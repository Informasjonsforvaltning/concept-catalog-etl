import json
from pymongo import MongoClient
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-o',
                    '--outputdirectory',
                    help="the path to the directory of the output files",
                    required=True)
args = parser.parse_args()
connection = MongoClient(
    f"""mongodb://{input("Username: ")}:{input("Password: ")}@localhost:27017/concept-catalogue?authSource=admin&authMechanism=SCRAM-SHA-1""")
db = connection["concept-catalogue"]


def get_affected_concepts(fagområde_list):
    if fagområde_list is None or len(fagområde_list) == 0:
        return False
    elif fagområde_list[0] in affected_fagomraader:
        return True
    else:
        return False


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


affected_fagomraader = ["ddf060fe-8935-3f4c-845a-58e055d2b246", "20b2e0cc-9fe1-11e5-a9f8-e4115b280940", "410ab733-9202-11e6-8b61-82ab1fa1f30b", "d329ded3-253e-f84d-be15-b50c5dded15b", "120b2e0e3-9fe1-11e5-a9f8-e4115b2809408"]
extracted_concepts = list(db.begrep.find({"ansvarligVirksomhet._id": "974761076", "fagområdeKoder": {"$in": affected_fagomraader}}))
affected_concepts = {}


for id_dict in extracted_concepts:
    _id = id_dict["_id"]
    fagomraadeKoder = id_dict.get("fagområdeKoder")
    if get_affected_concepts(fagomraadeKoder):
        affected_concepts[_id] = {}
        affected_concepts[_id]["fagområdeKoder"] = fagomraadeKoder

with open(args.outputdirectory + 'extracted_concepts.json', 'w', encoding="utf-8") as outfile:
    json.dump(affected_concepts, outfile, ensure_ascii=False, indent=4)
