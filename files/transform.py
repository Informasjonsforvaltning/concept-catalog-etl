import json
import argparse
import re


parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()


def transform(c_file):
    concepts = openfile(c_file)
    transformed_concepts = {}
    transformed_count = 0
    for concept in concepts:
        result = transform_concept(concepts[concept])
        transformed_concepts[concept] = result
        transformed_count += 1
    return transformed_concepts


def transform_concept(concept):
    transformed_concept = concept
    transformed_concept["definisjon"]["kildebeskrivelse"]["kilde"] = modify_source(concept["definisjon"]["kildebeskrivelse"]["kilde"])
    return transformed_concept


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


def modify_source(source_list):
    for source in source_list:
        if source.get("tekst"):
            compare = source.get("tekst")
            source["tekst"] = re.match('^{\"?\'?no\"?\'?: ?\"?\'?(.*)(\"+|\'+)}$', str(source["tekst"])).group(1)
            diff = len(str(compare))-len(source["tekst"])
            if diff != 10:
                print("Wrong diff: " + str(diff))
                print("Original: " + str(compare))
                print(source["tekst"])

    return source_list


outputfileName = args.outputdirectory + "transformed_concepts.json"
concepts_file = args.outputdirectory + "affected_concepts.json"


with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(concepts_file), outfile, ensure_ascii=False, indent=4)
