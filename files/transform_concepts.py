import json
import argparse
import datetime
import sys

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
#  Internfelt:
#  «Teknisk begrepsnavn»:  - Vil ha som internfelt
#       Dette feltet bruker vi til å beskrive hvordan begrepet ser ut i LowerCamelCase.
#  «Kildetype» - Vil ha som internfelt
#  •	Kildetype er forhold til kilde: sitat fra kilde, basert på kilde eller egendefinert
#  «Ansvarlig organisatorisk enhet»: - interne felt
#  •	Dette er et internt felt vi skal fase ut over tid, men trenger til å begynne med.
#  •	Det er ikke det samme som ansvarligVirksomhet.
#  •	Tekstfelt
#  «Teknisk term» / «Egenskapsnavn» / «Forretningsbegrep» - interne felt
#  •	Disse feltene skal migreres over.
#  •	Det er interne felt for Skatteetaten.
#  «Forvaltningsmerknad» / «Beslutningskommentar»: - interne felt
#  •	Dette er felt vi på sikt skal vurdere å ta bort, men som det er viktig at vi migrerer nå.
#  •	Jeg tenker det beste er å få de inn som interne felt, på lik linje med andre interne felt.


def transform_concept(concept):
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
        "erPublisert": "false",  # TODO: Migrere skjultEksternt inn i denne
        "frarådetTerm": {
            "nb": getstrings(
                concept["term"]
                .get("properties")
                .get("http://www.w3.org/2004/02/skos/core#hiddenLabel", {})
                .get("value")
            )
        },
        "kildebeskrivelse": {
            "forholdTilKilde":
                mapkildetype(
                    concept["term"]
                    .get("properties")
                    .get("http://www.skatteetaten.no/schema/properties/sourceType", {})
                    .get("value")
                ),
            "kilde": geturitekst(getstrings(
                concept["term"]
                .get("properties")
                .get("http://www.skatteetaten.no/schema/properties/sourceOfDefinition", {})
                .get("value")
            ))
        },
        "merknad": {
            "nb": getstrings(
                concept["term"]
                .get("properties")
                .get("http://www.skatteetaten.no/schema/properties/conceptNote", {})
                .get("value")
            )
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


def getstrings(value):
    if value is not None:
        return value.split(";")
    else:
        return []


def geturitekst(string_list):
    return [{"tekst": string} for string in string_list]


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
