import json
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()


def transform():
    transformed_meta = {}
    fdk_meta = openfile(args.outputdirectory + "mongo_fdkMeta.json")
    skatt_meta = openfile(args.outputdirectory + "mongo_skattMeta.json")
    publish_ids = openfile(args.outputdirectory + "publish_ids.json")
    for concept_id in publish_ids:
        new_id_uri = os.environ['CONCEPT_CATALOG_URI'] + concept_id
        old_id_uri = "http:/begrepskatalogen/begrep/" + concept_id
        if new_id_uri in fdk_meta and old_id_uri in skatt_meta:
            skattMeta = skatt_meta[old_id_uri]
            transformed_meta[new_id_uri] = {}
            transformed_meta[new_id_uri]["fdkId"] = skattMeta["fdkId"]
            transformed_meta[new_id_uri]["issued"] = skattMeta["issued"]
    return transformed_meta


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


outputfileName = args.outputdirectory + "transformed_metadata.json"


with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(), outfile, ensure_ascii=False, indent=4)
