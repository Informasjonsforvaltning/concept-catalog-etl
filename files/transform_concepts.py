import json
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()


def transform(c_file):
    concepts = openfile(c_file)
    transformed_concepts = {}
    multiple_drafts = []
    for concept_key in concepts:
        originaltbegrep = concepts[concept_key]["originaltBegrep"]
        result = transform_concept(concepts[concept_key])
        if transformed_concepts.get(originaltbegrep) and result is not None:
            updated_list = transformed_concepts[originaltbegrep]
            updated_list.append(result)
            transformed_concepts[originaltbegrep] = updated_list
        elif result is not None:
            transformed_concepts[originaltbegrep] = [result]
    for originalId in transformed_concepts:
        if len(transformed_concepts[originalId]) > 1:
            multiple_drafts.append(originalId)
    return multiple_drafts


def transform_concept(concept):
    if concept["_id"] == concept["originaltBegrep"]:
        return None
    elif "PUBLISERT" == concept["status"]:
        return None
    else:
        return concept


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


concepts_file = args.outputdirectory + "mongo_concepts.json"
outputfileName = args.outputdirectory + "transformed_concepts.json"


with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(concepts_file), outfile, ensure_ascii=False, indent=4)
