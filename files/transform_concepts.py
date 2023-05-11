import json
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()


def transform(c_file):
    concepts = openfile(c_file)
    transformed_concepts = {}
    for concept_key in concepts:
        originaltbegrep = concepts[concept_key]["originaltBegrep"]
        result = transform_concept(concepts[concept_key])
        if transformed_concepts[originaltbegrep] and result:
            transformed_concepts[originaltbegrep] = transformed_concepts[originaltbegrep].append(result)
        elif result:
            transformed_concepts[originaltbegrep] = [result]
    return transformed_concepts


def transform_concept(concept):
    if concept["_id"] != concept["originaltBegrep"] or concept["status"] != "PUBLISERT":
        return concept
    else:
        return None


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


concepts_file = args.outputdirectory + "mongo_concepts.json"
outputfileName = args.outputdirectory + "transformed_concepts.json"


with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(concepts_file), outfile, ensure_ascii=False, indent=4)
