import json
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()


#  TODO:
# Finn _id = concept-catalog (..) mongo_id , og _id = identifikator fra mapping og extract
# Kopier fdkId og issued fra data.brreg til concept-catalog, og slett data.brreg element etter load

def transform(fdk_meta_file, brreg_meta_file):
    transformed_meta = {}
    with open(fdk_meta_file) as fdk_file:
        fdk_meta = json.load(fdk_file)
    with open(brreg_meta_file) as brreg_file:
        brreg_meta = json.load(brreg_file)

    return transformed_meta

outputfileName = args.outputdirectory + "transformed_metadata.json"
fdk_meta_file = args.outputdirectory + "mongo_fdkMeta.json"
brreg_meta_file = args.outputdirectory + "mongo_brregMeta.json"


with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(fdk_meta_file, brreg_meta_file), outfile, ensure_ascii=False, indent=4)