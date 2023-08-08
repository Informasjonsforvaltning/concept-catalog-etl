import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()


def transform(c_file):
    concepts = openfile(c_file)
    transformed_concepts = {}

    for concept in concepts:
        transformed_concept = {
            "_id": concept["_id"],
            "merknad": join_strings(concept["merknad"]),
            "eksempel": join_strings(concept["eksempel"])
        }
        transformed_concepts[concept["_id"]] = transformed_concept

    return transformed_concepts


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


def join_strings(langs):
    new_langs = {}
    for language in langs:
        new_langs[language] = ",".join(language)
    return new_langs


concepts_file = "brreg_concepts.json"
outputfileName = args.outputdirectory + "transformed_concepts.json"

with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(concepts_file), outfile, ensure_ascii=False, indent=4)
