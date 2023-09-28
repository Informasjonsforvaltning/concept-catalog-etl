import json
import argparse
import datetime
import os

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()


def transform(c_file):
    concepts = openfile(c_file)
    transformed_concepts = {}
    transformed_count = 0
    for concept in concepts:
        result = transform_concept(concept)
        transformed_concepts[result.get("_id")] = result
        transformed_count += 1
    print("Total number of transformed concepts: " + str(transformed_count))
    return transformed_concepts


def transform_concept(concept):
    transformed_concept = {
        "_id": concept["term"].get("identifier"),
        "_class": "no.fdk.concept_catalog.model.BegrepDBO",
        "ansvarligVirksomhet": {
            "_id": "974761076"
        },
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
        "definisjon": {
            "tekst": {
                "nb": concept["term"]
                .get("properties")
                .get("http://purl.org/dc/elements/1.1/description", {})
                .get("value")
            },
            "kildebeskrivelse": {
                "forholdTilKilde":
                    mapkildetype(
                        concept["term"]
                        .get("properties")
                        .get("http://www.skatteetaten.no/schema/properties/sourceType", {})
                        .get("value"),
                        concept["term"].get("identifier")
                    ),
                "kilde": [{
                    "uri":
                        concept["term"]
                        .get("properties")
                        .get("http://www.skatteetaten.no/schema/properties/urlSourceOfDefinition", {})
                        .get("value"),
                    "tekst":
                        concept["term"]
                        .get("properties")
                        .get("http://www.skatteetaten.no/schema/properties/sourceOfDefinition", {})
                        .get("value")
                    }]
            }
        },
        "eksempel": {
            "nb": getstrings(
                concept["term"]
                .get("properties")
                .get("http://www.w3.org/2004/02/skos/core#example", {})
                .get("value")
            )
        },
        "endringslogelement": {
            "endretAv":
                concept["term"]
                .get("properties")
                .get("http://www.skatteetaten.no/schema/properties/lastUpdatedBy")
                .get("value"),
            "endringstidspunkt":
                convert_date(
                    concept["term"]
                    .get("properties")
                    .get("http://www.skatteetaten.no/schema/properties/lastUpdated")
                    .get("value")
                )
        },
        "erPublisert": "false",
        "fagområdeKoder": get_fagomraade(concept["term"]["vocabIdentifier"]),
        "definisjonForAllmennheten": {
            "tekst": {
                "nb":
                    concept["term"]
                    .get("properties")
                    .get("http://www.skatteetaten.no/schema/properties/popularExplanation")
                    .get("value")
            },
            "kildebeskrivelse": {
                "kilde": [{
                    "tekst":
                        concept["term"]
                        .get("properties")
                        .get("http://www.skatteetaten.no/schema/properties/sourceForPopularExplanation", {})
                        .get("value")
                }]
            }
        },
        "frarådetTerm": {
            "nb": getstrings(
                concept["term"]
                .get("properties")
                .get("http://www.w3.org/2004/02/skos/core#hiddenLabel", {})
                .get("value")
            )
        },
        "interneFelt": {
            # Ansvarlig organisatorisk enhet
            "337872c1-36e8-4d2c-a52c-bef0c0437b58": {
                "value": concept["term"]
                .get("properties")
                .get("http://www.skatteetaten.no/schema/properties/responsibleOrganisationalUnit", {})
                .get("value")
            },
            # Beslutningskommentar
            "7280610b-0fcd-4ec3-8da7-c7ad32fd76dc": {
                "value": concept["term"]
                .get("properties")
                .get("http://www.w3.org/2004/02/skos/core#changeNote", {})
                .get("value")
            },
            # Egenskapsnavn
            "cd68dbc3-eea4-4a47-bd1d-c0d7650222f8": {
                "value": convert_bool(
                    concept["term"]
                    .get("properties")
                    .get("http://www.skatteetaten.no/schema/properties/propertyName", {})
                    .get("value")
                )
            },
            # Forretningsbegrep
            "76fed193-c34d-469f-b38d-6a236f247fcc": {
                "value": convert_bool(
                    concept["term"]
                    .get("properties")
                    .get("http://www.skatteetaten.no/schema/properties/businessConcept", {})
                    .get("value")
                )
            },
            # Forvaltningsmerknad
            "ea21bbec-a262-4223-b234-09045c499098": {
                "value": concept["term"]
                .get("properties")
                .get("http://www.skatteetaten.no/schema/properties/forvaltningsmerknad", {})
                .get("value")
            },
            # Teknisk begrepsnavn
            "5dc1d0ba-1638-4ed8-b5b4-ea4fa43df5d3": {
                "value": concept["term"]
                .get("properties")
                .get("http://www.skatteetaten.no/schema/properties/tekniskTerm", {})
                .get("value")
            }
        },
        "merknad": {
            "nb":
                concept["term"]
                .get("properties")
                .get("http://www.skatteetaten.no/schema/properties/conceptNote", {})
                .get("value")
        },
        "originaltBegrep": concept["term"].get("identifier"),
        "definisjonForSpesialister": {
            "tekst": {
                "nb":
                    "Jurist: " +
                    concept["term"]
                    .get("properties")
                    .get("http://www.skatteetaten.no/schema/properties/legalExplanation")
                    .get("value") if
                    concept["term"]
                    .get("properties")
                    .get("http://www.skatteetaten.no/schema/properties/legalExplanation")
                    .get("value") is not None else None
            },
        },
        "statusURI": set_status_uri(
            concept["term"]
            .get("properties")
            .get("http://www.skatteetaten.no/schema/properties/conceptstatus", {})
            .get("value")
        ),
        "tillattTerm": {
            "nb": getstrings(
                    concept["term"]
                    .get("properties")
                    .get("http://www.w3.org/2004/02/skos/core#altLabel", {})
                    .get("value")
            )
        },
        "versjonsnr": {
            "major": 0,
            "minor": 0,
            "patch": 1
        },
        "gyldigFom":
            convert_date(
                concept["term"]
                .get("properties")
                .get("http://www.skatteetaten.no/schema/properties/validFrom", {})
                .get("value")
            ),
        "gyldigTom":
            convert_date(
                concept["term"]
                .get("properties")
                .get("http://www.skatteetaten.no/schema/properties/validTo", {})
                .get("value")
            )
    }
    if (concept["term"].get("properties").get("http://www.skatteetaten.no/schema/properties/nonPublic", {}).get("value").lower()) == "nei":
        listObj = openfile(publish_ids) if os.path.isfile(publish_ids) else []
        listObj.append(concept["term"].get("identifier"))
        with open(publish_ids, 'w', encoding="utf-8") as publish_file:
            json.dump(listObj, publish_file, ensure_ascii=False, indent=4)

    return remove_empty_from_dict(transformed_concept)


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


def remove_empty_from_dict(d):
    if type(d) is dict:
        new_dict = {}
        for k, v in d.items():
            tmp_v = remove_empty_from_dict(v)
            if should_keep_value(tmp_v):
                new_dict[k] = tmp_v
        if len(new_dict) > 0:
            return new_dict
    elif type(d) is list:
        new_list = []
        for v in d:
            tmp_v = remove_empty_from_dict(v)
            if should_keep_value(tmp_v):
                new_list.append(tmp_v)
        if len(new_list) > 0:
            return new_list
    else:
        return d


def should_keep_value(value):
    if type(value) is dict or type(value) is list:
        return len(value) > 0
    else:
        return value is not None


def convert_bool(string_value):
    if string_value:
        if string_value.lower() == "ja":
            return "true"
        elif string_value.lower() == "nei":
            return "false"
        else:
            print("Warning - Expected boolean value is not ja/nei: " + string_value)
            print("Returning noneValue")
            return None
    else:
        return string_value


def get_fagomraade(guid):
    if guid in fagomraader:
        return [str(fagomraader[guid])]
    else:
        return []


def getstrings(value):
    if value is not None:
        return value.split(";")
    else:
        return []


def mapkildetype(kildetype, begrep_id):
    if kildetype == "sitat fra kilde":
        return "SITATFRAKILDE"
    elif kildetype == "basert på kilde":
        return "BASERTPAAKILDE"
    elif kildetype == "egendefinert":
        return "EGENDEFINERT"
    else:
        print("Unknown kildetype: " + str(kildetype) + " for begrep: " + str(begrep_id))
        return None


def set_status_uri(status):
    if status == "Utkast":
        return "http://publications.europa.eu/resource/authority/concept-status/DRAFT"
    elif status == "Registrert":
        return "http://publications.europa.eu/resource/authority/concept-status/DRAFT"
    elif status == "Høring":
        return "http://publications.europa.eu/resource/authority/concept-status/CANDIDATE"
    elif status == "Godkjent":
        return "http://publications.europa.eu/resource/authority/concept-status/CURRENT"
    elif status == "Klar til godkjenning":
        return "http://publications.europa.eu/resource/authority/concept-status/WAITING"
    elif status == "Kvalitetssikring":
        return "http://publications.europa.eu/resource/authority/concept-status/CANDIDATE"
    elif status == "Kvalifisert - formell og innholdsmessig korrekt":
        return "http://publications.europa.eu/resource/authority/concept-status/CANDIDATE"
    elif status == "Tilbaketrukket":
        return "http://publications.europa.eu/resource/authority/concept-status/RETIRED"
    elif status == "Under behandling":
        return "http://publications.europa.eu/resource/authority/concept-status/CANDIDATE"
    else:
        print("Unknown status: " + str(status))


def convert_date(dateobject):
    if dateobject:
        return datetime.datetime.strftime(
                datetime.datetime.strptime(dateobject, '%Y-%m-%d'),
                "%Y-%m-%dT%H:%M:%S.000Z")
    else:
        return None


concepts_file = "skatt_concepts.json"

with open("fagomraader_codelist_mapping.json") as fd:
    fagomraader = json.load(fd)

outputfileName = args.outputdirectory + "transformed_concepts.json"
publish_ids = args.outputdirectory + "publish_ids.json"

with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(concepts_file), outfile, ensure_ascii=False, indent=4)
