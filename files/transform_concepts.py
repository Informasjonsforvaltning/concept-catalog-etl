import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()


def transform(c_file):
    concepts = openfile(c_file)
    transformed_concepts = {}

    for key in concepts:
        concept = concepts[key]
        transformed_concept = {
            "merknad": join_strings(concept.get("merknad")),
            "eksempel": join_strings(concept.get("eksempel"))
        }
        transformed_concepts[key] = transformed_concept

    return transformed_concepts


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


def join_strings(langs):
    new_langs = {}
    if langs:
        for language in langs:
            new_langs[language] = ",".join(langs[language])
        return new_langs
    else:
        return langs


concepts_file = args.outputdirectory + "mongo_concepts.json"
outputfileName = args.outputdirectory + "transformed_concepts.json"

with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(concepts_file), outfile, ensure_ascii=False, indent=4)
