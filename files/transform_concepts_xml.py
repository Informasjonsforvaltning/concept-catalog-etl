import json
import argparse
import datetime
import os
import xmltodict

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()


def transform(c_file):
    concepts = openfile(c_file)
    transformed_concepts = {}
    transformed_count = 0
    for concept in concepts["begrepCollection"]["begrepMember"]:
        result = transform_concept(concept)
        transformed_concepts[result.get("_id")] = result
        transformed_count += 1
    print("Total number of transformed concepts: " + str(transformed_count))
    return transformed_concepts


def transform_concept(concept):
    transformed_concept = {
        "_id": concept["identifier"],
        "_class": "no.fdk.concept_catalog.model.BegrepDBO",
        "ansvarligVirksomhet": {
            "_id": "974761076"
        },
        "anbefaltTerm": {
            "navn": {
                "nb": concept.get("prefLabel", {}).get("no"),
                "en": concept.get("prefLabel", {}).get("en"),
                "nn": concept.get("prefLabel", {}).get("nn")
            }
        },
        "definisjon": {
            "tekst": {
                "nb": concept.get("definition", {}).get("no")
            },
            "kildebeskrivelse": {
                "forholdTilKilde":
                    mapkildetype(
                        concept.get("sourceType"),
                        concept["identifier"]
                    ) if concept.get("sourceOfDefinition") is not None else None,
                "kilde": [{
                    "uri":
                        concept.get("urlSourceOfDefinition"),
                    "tekst":
                        concept.get("sourceOfDefinition")
                    }]
            }
        },
        "eksempel": {
            "nb": getstrings(
                concept.get("example", {})
                .get("no")
            )
        },
        "endringslogelement": {
            "endretAv":
                concept.get("lastUpdatedBy"),
            "endringstidspunkt":
                convert_date(
                    concept.get("lastUpdated")
                )
        },
        "erPublisert": "false",
        "fagområdeKoder": get_fagomraade(concept.get("subject")),
        "definisjonForAllmennheten": {
            "tekst": {
                "nb":
                    concept.get("popularExplanation", {})
                    .get("no")
            },
            "kildebeskrivelse": {
                "kilde": [{
                    "tekst":
                        concept
                        .get("sourceForPouplarExplanation", {})  # XML has typo in this field
                        .get("no")
                }]
            }
        },
        "frarådetTerm": {
            "nb": getstrings(
                concept.get("hiddenLabel", {})
                .get("no")
            )
        },
        "interneFelt": {
            # Ansvarlig organisatorisk enhet
            "337872c1-36e8-4d2c-a52c-bef0c0437b58": {
                "value":
                    concept.get("responsibleOrganisationalUnit")
            },
            # Beslutningskommentar
            "7280610b-0fcd-4ec3-8da7-c7ad32fd76dc": {
                "value":
                    concept.get("changeNote", {})
                    .get("no")
            },
            # Egenskapsnavn
            "cd68dbc3-eea4-4a47-bd1d-c0d7650222f8": {
                "value": convert_bool(
                    concept.get("propertyName")
                )
            },
            # Forretningsbegrep
            "76fed193-c34d-469f-b38d-6a236f247fcc": {
                "value": convert_bool(
                    concept.get("businessConcept")
                )
            },
            # Forvaltningsmerknad
            "ea21bbec-a262-4223-b234-09045c499098": {
                "value":
                    concept.get("forvaltningsmerknad", {})
                    .get("no")
            },
            # Teknisk begrepsnavn
            "5dc1d0ba-1638-4ed8-b5b4-ea4fa43df5d3": {
                "value":
                    concept.get("tekniskTerm", {})
                    .get("no")
            }
        },
        "merknad": {
            "nb":
                concept.get("conceptNote", {})
                .get("no")
        },
        "originaltBegrep": concept["identifier"],
        "definisjonForSpesialister": {
            "tekst": {
                "nb":
                    "Jurist: " +
                    concept.get("legalExplanation", {})
                    .get("no")
                    if
                    concept.get("legalExplanation", {})
                    .get("no") is not None
                    else None
            },
        },
        "statusURI": set_status_uri(
            concept.get("conceptStatus")
        ),
        "tillattTerm": {
            "nb": getstrings(
                concept.get("altLabel", {})
                .get("no")
            )
        },
        "versjonsnr": {
            "major": 0,
            "minor": 0,
            "patch": 1
        },
        "gyldigFom":
            convert_date(
                concept.get("validFrom")
            ),
        "gyldigTom":
            convert_date(
                concept.get("validTo")
            )
    }
    publishable_status = ["godkjent", "kvalifisert - formell og innholdsmessig korrekt"]
    if concept.get("nonPublic").lower() == "nei" and concept.get("conceptStatus").lower() in publishable_status:
        listObj = openfile(publish_ids) if os.path.isfile(publish_ids) else []
        listObj.append(concept.get("identifier"))
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


def get_fagomraade(fagomraade_string):
    if fagomraade_string in fagomraader:
        return [str(fagomraader[fagomraade_string])]
    else:
        return []


def getstrings(value):
    if value is not None:
        return value.split(";")
    else:
        return []


def mapkildetype(kildetype, begrep_id):
    if kildetype is None:
        return "BASERTPAAKILDE"
    elif kildetype.lower() in ["sitat fra kilde", "sitatfrakilde"]:
        return "SITATFRAKILDE"
    elif kildetype.lower() in ["basert på kilde", "basertpåkilde"]:
        return "BASERTPAAKILDE"
    elif kildetype.lower() == "egendefinert":
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


outputfileName = args.outputdirectory + "transformed_concepts.json"
publish_ids = args.outputdirectory + "publish_ids.json"
concepts_file = "skatt_concepts.json"
comments = args.outputdirectory + "skatt_comments.json"

with open(args.outputdirectory + "fagomraader_name_to_codelist.json") as fd:
    fagomraader = json.load(fd)

with open(args.outputdirectory + "komplett_uttrekk.xml") as fd:
    xml = xmltodict.parse(fd.read())

with open(concepts_file, 'w', encoding="utf-8") as outfile:
    json.dump(xml, outfile, ensure_ascii=False, indent=4)

with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(concepts_file), outfile, ensure_ascii=False, indent=4)
