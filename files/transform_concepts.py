import json
import argparse
import uuid
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()
namespace = uuid.uuid4()


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
# "Users: Hent users fra fil først, og kjør egen ETL til catalog-admin-service
# "History": Egen ETL til catalog-history-service når begrepene er lastet opp
# "Comments": Egen ETL til catalog-comments-service når begrepene er lastet opp
# "Offentlig tilgjengelig?" , se nedenfor
# Assignee - Tildelt - Krever populert liste over brukere
# Har de kilde til folkelig forklaring?

# Interne felt:
# "Ekstern begrepseier" ?
# "Forslag til fagområde" ? "forslag til fagområde er et enkelt tekstfelt"
# "Forkortelse" ?
# "Kilde til merknad" ? "Ikke strengt nødvendig, men da er det greit å få migrert denne informasjonen over til "kilde til definisjon"


def transform_concept(concept):
    mongo_id = str(uuid.uuid4())
    transformed_concept = {
        "_id": mongo_id,
        "_class": "no.fdk.concept_catalog.model.Begrep",
        "ansvarligVirksomhet": {
            "_id": "974760673"
        },
        "anbefaltTerm": {
            "navn": {
                "nb": concept["summary"]
            }
        },
        "erPublisert": "false",
        "bruksområde": {},
        "versjonsnr": {
            "major": 0,
            "minor": 0,
            "patch": 1
        },
        "opprettet": convert_date(concept["created"]),
        "opprettetAv": concept["reporter"],
        "originaltBegrep": mongo_id,
        "status": setstatus(concept.get("status")),
        "kontaktpunkt": {
            "harEpost": "informasjonsforvaltning@brreg.no",
            "harTelefon": "+47 75007500"
        },
        "tildeltBruker": getuser(concept["assignee"])
    }
    if len(concept["history"]) > 0:
        transformed_concept["endringslogelement"] = {
            "endretAv":
                getuser(concept["history"][-1]["author"])["name"],
            "endringstidspunkt":
                convert_date(concept["history"][-1]["created"])
        }
    else:
        transformed_concept["endringslogelement"] = {
            "endretAv":
                getuser(concept["history"][-1]["author"])["name"],
            "endringstidspunkt":
                convert_date(concept["created"])
        }

    for field in concept["customFieldValues"]:
        # Tillatt term
        if field["fieldName"] == "Alternativ term":
            tillattTerm = transformed_concept.get("tillattTerm", {})
            tillattTerm["nb"] = [
                field["value"]
            ]
            transformed_concept["tillattTerm"] = tillattTerm

        # This field does not seem to exist
        # if field["fieldName"] == "Term":
        #     term = transformed_concept.get("anbefaltTerm", {}).get("navn", {})
        #     term["nb"] = field["value"]
        #     transformed_concept["anbefaltTerm"] = term
        if field["fieldName"] == "Term engelsk":
            term = transformed_concept.get("anbefaltTerm", {})
            name = term.get("navn", {})
            name["en"] = field["value"]
            term["navn"] = name
            transformed_concept["anbefaltTerm"] = term
        if field["fieldName"] == "Term nynorsk":
            term = transformed_concept.get("anbefaltTerm", {})
            name = term.get("navn", {})
            name["nn"] = field["value"]
            term["navn"] = name
            transformed_concept["anbefaltTerm"] = term

        # Definisjon
        if field["fieldName"] == "Definisjon":
            definisjon = transformed_concept.get("definisjon", {})
            text = definisjon.get("tekst", {})
            text["nb"] = field["value"]
            definisjon["tekst"] = text
            transformed_concept["definisjon"] = definisjon
        if field["fieldName"] == "Definisjon engelsk":
            definisjon = transformed_concept.get("definisjon", {})
            text = definisjon.get("tekst", {})
            text["en"] = field["value"]
            definisjon["tekst"] = text
            transformed_concept["definisjon"] = definisjon
        if field["fieldName"] == "Definisjon nynorsk":
            definisjon = transformed_concept.get("definisjon", {})
            text = definisjon.get("tekst", {})
            text["nn"] = field["value"]
            definisjon["tekst"] = text
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
            definisjon = transformed_concept.get("definisjon", {})
            kildebeskrivelse = definisjon.get("kildebeskrivelse", {})
            kildebeskrivelse["forholdTilKilde"] = mapkildetype(field["value"])
            definisjon["kildebeskrivelse"] = kildebeskrivelse
            transformed_concept["definisjon"] = definisjon

        if field["fieldName"] == "Kilde til definisjon":
            definisjon = transformed_concept.get("definisjon", {})
            kildebeskrivelse = definisjon.get("kildebeskrivelse", {})
            kildebeskrivelse["kilde"] = geturitekst(getstrings(field["value"]))
            definisjon["kildebeskrivelse"] = kildebeskrivelse
            transformed_concept["definisjon"] = definisjon

        # Folkelig forklaring
        if field["fieldName"] == "Folkelig forklaring":
            folkeligForklaring = transformed_concept.get("folkeligForklaring", {})
            tekst = folkeligForklaring.get("tekst", {})
            tekst["nb"] = field["value"]
            folkeligForklaring["tekst"] = tekst
            transformed_concept["folkeligForklaring"] = folkeligForklaring

        # Merknad
        if field["fieldName"] == "Merknad":
            merknad = transformed_concept.get("merknad", {})
            merknad["nb"] = [
                field["value"]
            ]
            transformed_concept["merknad"] = merknad

        # TODO: Set status "erPublisert":
        #  Avvent å sette denne inntil vi har sikret at opprettede begrep er publiserbare
        # if field["fieldName"] == "Offentlig tilgjengelig":
        #     if len(field["value"]) > 1:
        #         print(str(concept["key"]) + ": Multiple values in Offentlig tilgjengelig")
        #     if (transformed_concept["status"] == "GODKJENT") and (field["value"][0] == "Ja"):
        #         transformed_concept["erPublisert"] = "true"

        # Gyldig fom/tom
        # ser ikke ut til å eksistere i Brreg-dataen

        # TildeltBruker (kodeliste)
        # tildelt = "uri til brukerkodeliste", gjøre oppslag mot admin-service basert på Assignee(brreg)

    return transformed_concept


def getuser(brreg_user):
    # TODO: Hent bruker fra admin-service, return brukerobjekt
    return {
        "id": uuid.uuid3(namespace, brreg_user),
        "name": brreg_user,
        "email": "work_in_progress@example.com"
    }


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
    elif status == "Høring":
        return "HOERING"
    else:
        return "UTKAST"


def convert_date(timestamp):
    if timestamp:
        # Remove milliseconds from timestamp
        datetime_object = datetime.fromtimestamp(timestamp/1000)
        return datetime.strftime(datetime_object, "%Y-%m-%dT%H:%M:%S.000Z")
    else:
        return None


concepts_file = "brreg_concepts.json"
outputfileName = args.outputdirectory + "transformed_concepts.json"

with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(concepts_file), outfile, ensure_ascii=False, indent=4)
