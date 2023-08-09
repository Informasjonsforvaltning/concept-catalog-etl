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
        transformed_fagomrade = join_values(concept.get("fagområde"), concept.get("bruksområde"))
        transformed_concept = {}
        if len(transformed_fagomrade) > 0:
            transformed_concept["fagområde"] = transformed_fagomrade
            transformed_concepts[key] = transformed_concept
    return transformed_concepts


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


def join_values(fagomrade, bruksomrade):
    new_fagomrade = {}
    if bruksomrade:
        for language in bruksomrade:
            new_fagomrade[language] = bruksomrade[language]
    if fagomrade:
        for language in fagomrade:
            if fagomrade[language] is not None:
                lang_list = new_fagomrade.get(language)
                if lang_list is None:
                    lang_list = []
                lang_list.append(fagomrade[language])
                new_fagomrade[language] = lang_list
    return new_fagomrade


concepts_file = args.outputdirectory + "mongo_concepts.json"
outputfileName = args.outputdirectory + "transformed_concepts.json"

with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(concepts_file), outfile, ensure_ascii=False, indent=4)
