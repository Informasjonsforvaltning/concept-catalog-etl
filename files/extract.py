import json
from pymongo import MongoClient
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument('-o',
                    '--outputdirectory',
                    help="the path to the directory of the output files",
                    required=True)
args = parser.parse_args()
connection = MongoClient(
    f"""mongodb://{input("Username: ")}:{input("Password: ")}@localhost:27017/concept-catalogue?authSource=admin&authMechanism=SCRAM-SHA-1""")
db = connection["concept-catalogue"]


def get_affected_concepts(source_list):
    if source_list is None:
        return False
    for source in source_list:
        if source.get("tekst"):
            if re.search('^{\"?\'?no\"?\'?: ?\"?\'?(.*)(\"+|\'+)}$', str(source["tekst"])) is not None:
                return True
    return False


extracted_concepts = list(db.begrep.find({"ansvarligVirksomhet._id": "974761076"}))
affected_concepts = {}
for id_dict in extracted_concepts:
    _id = id_dict["_id"]
    if get_affected_concepts(
            id_dict
            .get("definisjon", {})
            .get("kildebeskrivelse", {})
            .get("kilde")):
        affected_concepts[_id] = {}
        affected_concepts[_id]["definisjon"] = id_dict["definisjon"]

with open(args.outputdirectory + 'affected_concepts.json', 'w', encoding="utf-8") as outfile:
    json.dump(affected_concepts, outfile, ensure_ascii=False, indent=4)
