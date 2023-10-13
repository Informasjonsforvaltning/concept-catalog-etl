import json
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()


#  TODO:
# Finn _id = concept-catalog.(...)/mongo_id , og _id = identifikator fra mapping og extract
# Kopier fdkId og issued fra data.brreg til concept-catalog

def transform():
    transformed_meta = {}
    fdk_meta = openfile(args.outputdirectory + "mongo_fdkMeta.json")
    brreg_meta = openfile(args.outputdirectory + "mongo_brregMeta.json")
    transformed_concepts = openfile(args.outputdirectory + "transformed_concepts.json")
    publish_ids = openfile(args.outputdirectory + "publish_ids.json")
    mapped_identifiers = openfile(args.outputdirectory + "mapped_identifiers.json")
    for concept_id in publish_ids:
        term = transformed_concepts[concept_id]["anbefaltTerm"]["navn"]["nb"]
        fdk_id = os.environ['CONCEPT_CATALOG_URI'] + concept_id
        if term in mapped_identifiers and fdk_id in fdk_meta:
            brregMeta = brreg_meta[mapped_identifiers[term]]
            transformed_meta[fdk_id] = {}
            transformed_meta[fdk_id]["fdkId"] = brregMeta["fdkId"]
            transformed_meta[fdk_id]["issued"] = brregMeta["issued"]
    return transformed_meta


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


outputfileName = args.outputdirectory + "transformed_metadata.json"


with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(), outfile, ensure_ascii=False, indent=4)