import json
import argparse
import datetime

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

# TODO:
#  «Interesseområde»:
#  •	Interesseområde er Fagområde, som vi skal ha kodeliste på. Kanskje vi må snakkes om hvordan vi løser dette?
#  «Skjult eksternt»: - erPublisert
#  •	Skjult eksternt er et felt med boolske verdier, Ja betyr at begrepet ikke er publisert på FDK.
#  •	Skal brukes til Publiseringstilstand.


def transform_concept(concept):
    transformed_concept = {
        "_id": concept["term"].get("identifier"),
        "_class": "no.fdk.concept_catalog.model.BegrepDBO",
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
            },
            "kildebeskrivelse": {
                "forholdTilKilde":
                    mapkildetype(
                        concept["term"]
                        .get("properties")
                        .get("http://www.skatteetaten.no/schema/properties/sourceType", {})
                        .get("value")
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
        "erPublisert": "false",  # TODO: Migrere skjultEksternt inn i denne, med motsatt verdi, må sikre at begrepet er publiserbart
        "fagområde": {
            "nb": [
                concept["voc_names"][concept["term"]["vocabIdentifier"] + ":Skatteetaten"]["properties"]["http://purl.org/dc/elements/1.1/title"]["value"]
            ]
            #  TODO: Må kanskje ta høyde for om fagområde allerede finnes
            #   Ligger alle fagområder for alle begrep samlet i voc_names?
            #   Har alle strukturen vocabId:Skatteetaten?
            #   Skal være en kodeliste
        },
        "folkeligForklaring": {
            "tekst": {
                "nb":
                    concept["term"]
                    .get("properties")
                    .get("http://www.skatteetaten.no/schema/properties/popularExplanation")
                    .get("value")
            },
            "kildebeskrivelse": {
                "kilde": [{
                    concept["term"]
                    .get("properties")
                    .get("http://www.skatteetaten.no/schema/properties/sourceForPopularExplanation", {})
                    .get("value")
                }]
            }
        },
        # {"tekst": {"nb": "dette er en definisjon for allmennheten på det nye begrepet", "nn": "nynorsk ",
        #            "en": "engelsk"}, "kildebeskrivelse": {"forholdTilKilde": "EGENDEFINERT", "kilde": []}}
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
        "status": setstatus(
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
            )
        ,
        "gyldigTom":
            convert_date(
                concept["term"]
                .get("properties")
                .get("http://www.skatteetaten.no/schema/properties/validTo", {})
                .get("value")
            )
    }

    return transformed_concept


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


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


def getstrings(value):
    if value is not None:
        return value.split(";")
    else:
        return []


def mapkildetype(kildetype):
    if kildetype == "sitat fra kilde":
        return "SITATFRAKILDE"
    elif kildetype == "basert på kilde":
        return "BASERTPAAKILDE"
    elif kildetype == "egendefinert":
        return "EGENDEFINERT"
    else:
        return None


def setstatus(status):
    # TODO: Registrert = Utkast
    #  Kvalifisert - formell og innholdsmessig korrekt = Kvalitetssikring
    #  Tilbaketrukket = Utgått
    supported_status = ["UTKAST", "GODKJENT", "HOERING", "PUBLISERT"]
    if status.upper() in supported_status:
        return status.upper()
    else:
        return "UTKAST"


def convert_date(dateobject):
    if dateobject:
        return datetime.datetime.strftime(
                datetime.datetime.strptime(dateobject, '%Y-%m-%d'),
                "%Y-%m-%dT%H:%M:%S.000Z")
    else:
        return None


concepts_file = "skatt_concepts.json"
outputfileName = args.outputdirectory + "transformed_concepts.json"

with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(concepts_file), outfile, ensure_ascii=False, indent=4)
