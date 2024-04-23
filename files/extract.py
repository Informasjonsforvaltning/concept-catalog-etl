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


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


extracted_concepts = list(db.begrep.find({"ansvarligVirksomhet._id": "974761076"}))
concepts = {}
for id_dict in extracted_concepts:
    concepts[id_dict["_id"]] = {"statusURI": id_dict.get("statusURI"), "versjonsnr": id_dict.get("versjonsnr")}

with open(args.outputdirectory + 'extracted_concepts.json', 'w', encoding="utf-8") as outfile:
    json.dump(concepts, outfile, ensure_ascii=False, indent=4)
