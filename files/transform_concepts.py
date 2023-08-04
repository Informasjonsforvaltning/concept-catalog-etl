import json
import argparse
import os
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()


def transform(c_file):
    con_file = openfile(c_file)
    transformed_concepts = {}

    projects = con_file["projects"]
    project = next(prj for prj in projects if prj["name"] == "BEGREP")
    concepts = project["issues"]
    for concept in concepts:
        result = transform_concept(concept)
        transformed_concepts[result.get("_id")] = result

    return transformed_concepts

# TODO:
# "History": Egen ETL til catalog-history-service når begrepene er lastet opp
# "Offentlig tilgjengelig?" ? "Dette vil tilsvare publiseringstilstand hvis begrepet har godkjent; Hvis offentlig tilgjengelig er ja på et godkjent begrep skal begrepet ha publiseringstilstand "publisert". Hvis begrepet ikke har status godkjent kan vi se bort fra dette feltet. Hvis det er mulig."
# Assignee - Tildelt
# Har de kilde til folkelig forklaring?

# Interne felt:
# "Ekstern begrepseier" ? Internt felt
# "Forslag til fagområde" ? "forslag til fagområde er et enkelt tekstfelt"
# "Forkortelse" ?
# "Kilde til merknad" ? "Ikke strengt nødvendig, men da er det greit å få migrert denne informasjonen over til "kilde til definisjon"




def transform_concept(concept):
    transformed_concept = {
        "_class": "no.fdk.concept_catalog.model.Begrep",
        "ansvarligVirksomhet": {"_id": "974760673"},
        "endringslogelement": {
            "endretAv":
                concept["history"][-1]["author"],
            "endringstidspunkt":
                convert_date(concept["history"][-1]["created"])
        },
        "erPublisert": "false",
        "bruksområde": {},
        "versjonsnr": {
            "major": 0,
            "minor": 0,
            "patch": 1
        },
        "originaltBegrep": "$_id",  # Mulig dette ikke funker på create, evt loope igjennom alle og sette ID i etterkant --> db.begrep.update({}, [{"$set": {"originaltBegrep": "$_id"}}],{upsert:false,multi:true})
        "status": setstatus(concept.get("status")),
        "kontaktpunkt": {
            "harEpost": "informasjonsforvaltning@brreg.no",
            "harTelefon": "(+47)75007500"
        }
    }
    for field in concept["customFieldValues"]:
        # Tillatt term
        if field["fieldName"] == "Alternativ term":
            tillattTerm = transformed_concept.get("tillattTerm", {})
            tillattTerm["nb"] = [
                field["value"]
            ]
            transformed_concept["tillattTerm"] = tillattTerm

        if field["fieldName"] == "Term":
            term = transformed_concept.get("anbefaltTerm", {}).get("navn", {})
            term["nb"] = field["value"]
            transformed_concept["anbefaltTerm"] = term
        if field["fieldName"] == "Term engelsk":
            term = transformed_concept.get("anbefaltTerm", {}).get("navn", {})
            term["en"] = field["value"]
            transformed_concept["anbefaltTerm"] = term
        if field["fieldName"] == "Term nynorsk":
            term = transformed_concept.get("anbefaltTerm", {}).get("navn", {})
            term["nn"] = field["value"]
            transformed_concept["anbefaltTerm"] = term

        # Definisjon
        if field["fieldName"] == "Definisjon":
            definisjon = transformed_concept.get("definisjon", {}).get("tekst", {})
            definisjon["nb"] = field["value"]
            transformed_concept["definisjon"] = definisjon
        if field["fieldName"] == "Definisjon engelsk":
            definisjon = transformed_concept.get("definisjon", {}).get("tekst", {})
            definisjon["en"] = field["value"]
            transformed_concept["definisjon"] = definisjon
        if field["fieldName"] == "Definisjon nynorsk":
            definisjon = transformed_concept.get("definisjon", {}).get("tekst", {})
            definisjon["nn"] = field["value"]
            transformed_concept["definisjon"] = definisjon

        # Eksempel
        if field["fieldName"] == "Eksempel":
            eksempel = transformed_concept.get("eksempel", {})
            eksempel["nb"] = [
                field["value"]
            ]
            transformed_concept["eksempel"] = eksempel

        # Fagområde
        if field["fieldName"] == "Fagområde":
            subject_area = transformed_concept.get("fagområde", {})
            subject_area["nb"] = field["value"]
            transformed_concept["fagområde"] = subject_area

        # FrarådetTerm
        if field["fieldName"] == "Frarådet term":
            unadvisedTerm = transformed_concept.get("frarådetTerm", {})
            unadvisedTerm["nb"] = [
                field["value"]
            ]
            transformed_concept["frarådetTerm"] = unadvisedTerm

        if field["fieldName"] == "Forhold til kilde":
            transformed_concept["definisjon"]["kildebeskrivelse"]["forholdTilKilde"]: mapkildetype(field["value"])

        if field["fieldName"] == "Kilde til definisjon":
            transformed_concept["definisjon"]["kildebeskrivelse"]["kilde"]: geturitekst(getstrings(field["value"]))

        # Folkelig forklaring
        if field["fieldName"] == "Folkelig forklaring":
            folkelig_forklaring = transformed_concept.get("folkeligForklaring", {})
            folkelig_forklaring["tekst"]["nb"] = field["value"]
            transformed_concept["folkeligForklaring"] = folkelig_forklaring

        # Merknad
        if field["fieldName"] == "Merknad":
            merknad = transformed_concept.get("merknad", {})
            merknad["nb"] = [
                field["value"]
            ]
            transformed_concept["merknad"] = merknad

        # Gyldig fom/tom
        # ser ikke ut til å eksistere i Brreg-dataen


        # TildeltBruker (kodeliste)
        # tildelt = "uri til brukerkodeliste", gjøre oppslag mot admin-service basert på Assignee(brreg)

    return transformed_concept


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


def mapkildetype(kildetype):
    if kildetype.lower() == "sitat fra kilde":
        return "SITATFRAKILDE"
    elif kildetype.lower() == "basert på kilde":
        return "BASERTPAAKILDE"
    elif kildetype.lower() == "egendefinert":
        return "EGENDEFINERT"
    else:
        return None


def geturitekst(string_list):
    return [{"tekst": string} for string in string_list]


def getstrings(value):
    if value is not None:
        return value.split(";")
    else:
        return []


def setstatus(status):
    supported_status = ["UTKAST", "GODKJENT", "HOERING", "PUBLISERT"]
    if status.upper() in supported_status:
        return status.upper()
    else:
        return "UTKAST"


def convert_date(timestamp_string):
    if timestamp_string:
        datetime_object = datetime.fromtimestamp(timestamp_string)
        return datetime.strftime(datetime_object, "%Y-%m-%dT%H:%M:%S.000Z")
    else:
        return None


concepts_file = "brreg_concepts.json"
outputfileName = args.outputdirectory + "transformed_concepts.json"

with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(concepts_file), outfile, ensure_ascii=False, indent=4)
