import json
import argparse
import os


parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()
old_base_uri = os.environ['OLD_BASE_URI']
new_base_uri = os.environ['NEW_BASE_URI']
really_old_base_uri = os.environ['OLD_BASE_URI']


def transform(c_file):
    concepts = openfile(c_file)
    transformed_concepts = {}
    transformed_count = 0
    failed_count = 0
    failed = {}
    for concept_key in concepts:
        result = transform_concept(concepts[concept_key])
        if result["transformed"]:
            transformed_concepts[concept_key] = result["transformed"]
            transformed_count += 1
        else:
            failed[concept_key] = concepts[concept_key]
            failed_count += 1
    print("Total number of transformed concepts: " + str(transformed_count))
    print("Total number of non-transformed concepts: " + str(failed_count))
    with open(args.outputdirectory + "not_transformed.json", 'w', encoding="utf-8") as err_file:
        json.dump(failed, err_file, ensure_ascii=False, indent=4)
    return transformed_concepts


def transform_concept(concept):
    see_also = concept.get("seOgså")
    see_also = see_also if see_also else []
    new_see_also = []
    has_been_modified = False
    for url in see_also:
        modified_url = replace_url(url)
        if modified_url:
            has_been_modified = True
            new_see_also.append(modified_url)
        else:
            new_see_also.append(url)
    if has_been_modified:
        transformed_concept = concept
        transformed_concept["seOgså"] = new_see_also
        return {"transformed": transformed_concept}
    else:
        return {"transformed": None}


def replace_url(url):
    if old_base_uri in url:
        return url.replace(old_base_uri, f'{new_base_uri}/collections')
    elif really_old_base_uri in url:
        return url.replace(really_old_base_uri, f'{new_base_uri}/collections')
    return None


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


concepts_file = args.outputdirectory + "mongo_concepts.json"
outputfileName = args.outputdirectory + "transformed_concepts.json"


with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(concepts_file), outfile, ensure_ascii=False, indent=4)
