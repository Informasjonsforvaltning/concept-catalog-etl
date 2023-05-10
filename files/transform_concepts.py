import json
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()


def transform(c_file):
    concepts = openfile(c_file)
    transformed_concepts = {}
    transformed_count = 0
    failed = {}
    for concept in concepts:
        result = transform_concept(concept)
        transformed_concepts[result.get("_id")] = result
    #        transformed_count += 1
    # print("Total number of transformed concepts: " + str(transformed_count))
    # with open("not_transformed.json", 'w', encoding="utf-8") as err_file:
    #     json.dump(failed, err_file, ensure_ascii=False, indent=4)
    return transformed_concepts


def transform_concept(concept):
    # Status er ikke 1-1, vi har enum UTKAST, GODKJENT, HOERING, PUBLISERT
    # Hva er vår term teknisk begrepsnavn? (tillattTerm? Datastrukturterm?)

    transformed_concept = {
        "_id": concept.term.get("identifier"),
        "_class": "no.fdk.concept_catalog.model.Begrep",
        "anbefaltTerm": {
            "navn": {
                "nb": concept.term.properties.get("value"),
                "en": concept.term.localisedProperties
                .get("http:\/\/purl.org\/dc\/elements\/1.1\/title", {})
                .get("English (United Kingdom)", {}).get("value"),
                "nn": concept.term.localisedProperties
                .get("http:\/\/purl.org\/dc\/elements\/1.1\/title", {})
                .get("Norwegian Nynorsk", {}).get("value"),
            }
        },
        "ansvarligVirksomhet": {"_id": "974761076"},
        "bruksområde": {},
        "definisjon": {
            "tekst": {
                "nb": concept.term.properties
                .get("http:\/\/purl.org\/dc\/elements\/1.1\/description",{})
                .get("value")
            }
        }

    }

    return transformed_concept


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


concepts_file = args.outputdirectory + "skatt_concepts.json"
outputfileName = args.outputdirectory + "transformed_concepts.json"

with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(concepts_file), outfile, ensure_ascii=False, indent=4)
