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

# Finn unike ID'er fra internSeOgså, internErstattesAv, internBegrepsRelasjon.relatertBegrep
# Opprett dict med ID'er, der value er liste over _id som den unike ID'en er hentet fra
# Gjør nytt uttrekk fra begrep med listen over, opprett ny liste med begrep som er true i erPublisert
# Hvis den listen ikke er tom, så må vi finne begrepene som inneholder disse ID'ene

# Fil_1 : ID'ene som har blitt publisert
# Fil_2: Begrep som har et av begrepene i fil_1 som intern relasjon


#seOgså
#erstattesAv
#begrepsRelasjon (obj)


extracted_concepts = list(db.begrep.find())
intern_relation_concepts = {}
published_concepts = []
affected_concepts = {}

for id_dict in extracted_concepts:
    concept_id = id_dict["_id"]
    internSeeAlso = id_dict.get("internSeOgså", [])
    internErstattesAv = id_dict.get("internErstattesAv", [])
    internBegrepsRelasjon = id_dict.get("internBegrepsRelasjon", [])

    for internSeeAlso_id in internSeeAlso:
        if internSeeAlso_id not in intern_relation_concepts:
            intern_relation_concepts[internSeeAlso_id] = [concept_id]
        else:
            intern_relation_concepts[internSeeAlso_id].append(concept_id)

    for internErstattesAv_id in internErstattesAv:
        if internErstattesAv_id not in intern_relation_concepts:
            intern_relation_concepts[internErstattesAv_id] = [concept_id]
        else:
            intern_relation_concepts[internErstattesAv_id].append(concept_id)

    for internBegrepsRelasjon_dict in internBegrepsRelasjon:
        internBegrepsRelasjon_id = internBegrepsRelasjon_dict.get("relatertBegrep")
        if internBegrepsRelasjon_id is not None:
            if internBegrepsRelasjon_id not in intern_relation_concepts:
                intern_relation_concepts[internBegrepsRelasjon_id] = [concept_id]
            else:
                intern_relation_concepts[internBegrepsRelasjon_id].append(concept_id)

for id_dict in extracted_concepts:
    concept_id = id_dict["_id"]
    isPublished = id_dict.get("erPublisert", False)
    if concept_id in intern_relation_concepts and isPublished:
        published_concepts.append(concept_id)

for id_dict in extracted_concepts:
    concept_id = id_dict["_id"]
    if concept_id in published_concepts:
        affected_concepts[concept_id] = id_dict


with open(args.outputdirectory + 'published_concepts.json', 'w', encoding="utf-8") as outfile:
    json.dump(published_concepts, outfile, ensure_ascii=False, indent=4)

with open(args.outputdirectory + 'affected_concepts.json', 'w', encoding="utf-8") as outfile:
    json.dump(affected_concepts, outfile, ensure_ascii=False, indent=4)
