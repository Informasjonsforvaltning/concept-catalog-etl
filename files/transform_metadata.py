import json
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()


# Finn _id = concept-catalog.(...)/mongo_id , og _id = identifikator fra mapping og extract
# Kopier fdkId og issued fra data.brreg til concept-catalog

def transform():
    transformed_meta = {}
    fdk_meta = openfile(args.outputdirectory + "mongo_fdkMeta.json")
    brreg_meta = openfile(args.outputdirectory + "mongo_brregMeta.json")
    publish_ids = openfile(args.outputdirectory + "publish_ids.json")
    fdkId_mapping = openfile(args.outputdirectory + "fdkId_mapping.json")
    for concept_id in publish_ids:
        fdk_id = os.environ['CONCEPT_CATALOG_URI'] + concept_id
        if fdk_id in fdk_meta:
            brreg_id = fdkId_mapping[concept_id]
            brregMeta = brreg_meta[brreg_id]
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