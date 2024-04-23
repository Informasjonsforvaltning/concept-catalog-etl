import json
import argparse
import re


parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()


def get_correct_fagomraade(_id):
    for concept in migrate_file:
        if concept["identifier"] == _id:
            return [convert_file.get(concept["subject"])]
    return False


def transform(c_file):
    concepts = openfile(c_file)
    transformed_concepts = {}
    transformed_count = 0
    for concept in concepts:
        result = transform_concept(concept, concepts[concept])
        if result:
            transformed_concepts[concept] = result
            transformed_count += 1
    print("Total number of transformed concepts (should be 189): " + str(transformed_count))
    return transformed_concepts


def transform_concept(_id, concept):
    transformed_concept = concept
    check_fagomraade = get_correct_fagomraade(_id)
    if concept["fagområdeKoder"][0] != check_fagomraade[0]:
        print("Identifier: " + _id + " ||| " + "Concept fagområde: " + concept["fagområdeKoder"][0] + " ||| " + "Check fagområde: " + check_fagomraade[0])
        transformed_concept["fagområdeKoder"] = get_correct_fagomraade(_id)
        return transformed_concept
    else:
        return None


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


outputfileName = args.outputdirectory + "transformed_concepts.json"
concepts_file = args.outputdirectory + "extracted_concepts.json"
migrate_file = openfile(args.outputdirectory + "skatt_concepts.json")
convert_file = openfile(args.outputdirectory + "fagomraader_name_to_codelist.json")

with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(concepts_file), outfile, ensure_ascii=False, indent=4)
