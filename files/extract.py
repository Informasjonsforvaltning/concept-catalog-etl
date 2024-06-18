import json
from datetime import datetime

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
affected_concept_ids = []
affected_concepts = {}

for id_dict in extracted_concepts:
    concept_id = id_dict["_id"]
    internSeeAlso = id_dict.get("internSeOgså", [])
    internErstattesAv = id_dict.get("internErstattesAv", [])
    internBegrepsRelasjon = id_dict.get("internBegrepsRelasjon", [])

    for internSeeAlso_id in internSeeAlso:
        lst = intern_relation_concepts.get(internSeeAlso_id, [])
        lst.append(concept_id)
        intern_relation_concepts[internSeeAlso_id] = lst

    for internErstattesAv_id in internErstattesAv:
        lst = intern_relation_concepts.get(internErstattesAv_id, [])
        lst.append(concept_id)
        intern_relation_concepts[internErstattesAv_id] = lst

    for internBegrepsRelasjon_dict in internBegrepsRelasjon:
        internBegrepsRelasjon_id = internBegrepsRelasjon_dict.get("relatertBegrep")
        lst = intern_relation_concepts.get(internBegrepsRelasjon_id, [])
        lst.append(concept_id)
        intern_relation_concepts[internBegrepsRelasjon_id] = lst

for id_dict in extracted_concepts:
    concept_id = id_dict["_id"]
    isPublished = id_dict.get("erPublisert", False)
    if concept_id in intern_relation_concepts and isPublished is True:
        published_concepts.append(concept_id)

for relation_id in intern_relation_concepts:
    if relation_id in published_concepts:
        for concept_id in intern_relation_concepts[relation_id]:
            affected_concept_ids.append(concept_id)


for id_dict in extracted_concepts:
    concept_id = id_dict["_id"]
    if concept_id in affected_concept_ids:
        affected_concepts[concept_id] = id_dict


def datetime_serializer(obj):
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%dT%H:%M:%S.%fZ')


with open(args.outputdirectory + 'published_concepts.json', 'w', encoding="utf-8") as outfile:
    json.dump(published_concepts, outfile, ensure_ascii=False, indent=4, default=datetime_serializer)

with open(args.outputdirectory + 'affected_concepts.json', 'w', encoding="utf-8") as outfile:
    json.dump(affected_concepts, outfile, ensure_ascii=False, indent=4, default=datetime_serializer)
