import json
import argparse
import os
import datetime

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
    # Hva er vår term teknisk begrepsnavn? (Datastrukturterm?)
    # Hva er folkelig forklaring?

    transformed_concept = {
        "_id": concept["term"].get("identifier"),
        "_class": "no.fdk.concept_catalog.model.Begrep",
        "anbefaltTerm": {
            "navn": {
                "nb": concept["term"]
                .get("properties")
                .get("http://purl.org/dc/elements/1.1/title")
                .get("value"),
                "en": concept["term"]
                .get("localisedProperties")
                .get("http://purl.org/dc/elements/1.1/title", {})
                .get("English (United Kingdom)", {})
                .get("value"),
                "nn": concept["term"]
                .get("localisedProperties")
                .get("http://purl.org/dc/elements/1.1/title", {})
                .get("Norwegian Nynorsk", {}).get("value"),
            }
        },
        "ansvarligVirksomhet": {"_id": "974761076"},
        "bruksområde": {},
        "definisjon": {
            "tekst": {
                "nb": concept["term"]
                .get("properties")
                .get("http://purl.org/dc/elements/1.1/description", {})
                .get("value")
            }
        },
        "eksempel": {
            "nb": [
                concept["term"]
                .get("properties")
                .get("http://www.w3.org/2004/02/skos/core#example", {})
                .get("value")
            ]
        },
        "erPublisert": "false",
        "frarådetTerm": {
            "nb": [
                concept["term"]
                .get("properties")
                .get("http://www.w3.org/2004/02/skos/core#hiddenLabel", {})
                .get("value")
            ]
        },
        "kildebeskrivelse": {
            "forholdTilKilde":
                concept["term"]
                .get("properties")
                .get("http://www.skatteetaten.no/schema/properties/sourceType", {})
                .get("value"),
            "kilde": [
                concept["term"]
                .get("properties")
                .get("http:\/\/www.skatteetaten.no\/schema\/properties\/sourceOfDefinition", {})
                .get("value")
                ]
        },
        "merknad": {
            "nb": [
                concept["term"]
                .get("properties")
                .get("http:\/\/www.skatteetaten.no\/schema\/properties\/conceptNote", {})
                .get("value")
            ]
        },
        "originaltBegrep": concept["term"].get("identifier"),
        "status": setstatus(
            concept["term"]
            .get("properties")
            .get("http://www.skatteetaten.no/schema/properties/conceptstatus", {})
            .get("value")
        ),
        "tillattTerm": {  # TODO
            "nb": [
                ""
            ]
        },
        "versjonsnr": {
            "major": 0,
            "minor": 0,
            "patch": 1
        },
        "gyldigFom": {
            "$date": convert_date(
                concept["term"]
                .get("properties")
                .get("http://www.skatteetaten.no/schema/properties/validFrom", {})
                .get("value")
            )
        },
        "gyldigTom": {
            "$date": convert_date(
                concept["term"]
                .get("properties")
                .get("http://www.skatteetaten.no/schema/properties/validTo", {})
                .get("value")
            )
        }
    }

    return transformed_concept


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


def setstatus(status):
    supported_status = ["UTKAST", "GODKJENT", "HOERING", "PUBLISERT"]
    if status.upper() in supported_status:
        return status.upper()
    else:
        return "UTKAST"


def convert_date(date):  # TODO
    utc_date = date.astimezone(datetime.timezone.utc)
    return utc_date


concepts_file = "skatt_concepts.json"
outputfileName = args.outputdirectory + "transformed_concepts.json"

with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(concepts_file), outfile, ensure_ascii=False, indent=4)
