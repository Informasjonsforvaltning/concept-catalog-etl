import json
import argparse
import uuid
import random
from datetime import datetime
import os.path

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()
rd = random.Random()
rd.seed(0)


def transform(u_file):
    con_file = openfile(u_file)
    transformed_concepts = {}
    comments_filename = args.outputdirectory + "brreg_comments.json"
    history_filename = args.outputdirectory + "brreg_history.json"
    comments = {}
    history = {}

    projects = con_file["projects"]
    project = next(prj for prj in projects if prj["name"] == "BEGREP")
    concepts = project["issues"]
    for concept in concepts:
        mongo_id = str(uuid.UUID(int=rd.getrandbits(128), version=4))
        result = transform_concept(concept, mongo_id)
        transformed_concepts[mongo_id] = result
        if concept.get("comments") is not None:
            comments[mongo_id] = concept["comments"]
        if concept.get("history") is not None:
            history[mongo_id] = concept["history"]

    with open(comments_filename, 'w', encoding="utf-8") as brreg_comments_file:
        json.dump(comments, brreg_comments_file, ensure_ascii=False, indent=4)
    with open(history_filename, 'w', encoding="utf-8") as brreg_history_file:
        json.dump(history, brreg_history_file, ensure_ascii=False, indent=4)

    return transformed_concepts

# TODO:
# "Offentlig tilgjengelig?" , se nedenfor


def transform_concept(concept, mongo_id):
    transformed_concept = {
        "_id": mongo_id,
        "_class": "no.fdk.concept_catalog.model.BegrepDBO",
        "ansvarligVirksomhet": {
            "_id": "974760673"
        },
        "anbefaltTerm": {
            "navn": {
                "nb": concept["summary"]
            }
        },
        "erPublisert": "false",
        "versjonsnr": {
            "major": 0,
            "minor": 0,
            "patch": 1
        },
        "opprettet": convert_date(concept["created"]),
        "opprettetAv": concept["reporter"],
        "originaltBegrep": mongo_id,
        "statusURI": set_status(concept.get("status")),
        "kontaktpunkt": {
            "harEpost": "informasjonsforvaltning@brreg.no",
            "harTelefon": "+47 75007500"
        },
        "assignedUser": getuser(concept["assignee"])["_id"] if concept.get("assignee") and getuser(concept["assignee"]) is not None else None
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

        # Begrepseier (internfelt)
        if field["fieldName"] == "Begrepseier":
            internal_fields = transformed_concept.get("interneFelt", {})
            owner = intern_begrepseier.get(field["value"])
            if owner:
                internal_fields["8317e9b4-ec05-470a-9f94-deb12d87f033"] = {
                    "value": owner
                }
            else:
                print(str(concept["key"]) + ": Unknown owner: " + field["value"])
            transformed_concept["interneFelt"] = internal_fields

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

        # Ekstern begrepseier (internfelt)
        if field["fieldName"] == "Ekstern begrepseier":
            internal_fields = transformed_concept.get("interneFelt", {})
            ext_owner = ekstern_begrepseier.get(field["value"])
            if ext_owner:
                internal_fields["0da72785-ede5-49ab-b2de-20f7790320f0"] = {
                    "value": ext_owner
                }
            else:
                print(str(concept["key"]) + ": Unknown external owner: " + field["value"])
            transformed_concept["interneFelt"] = internal_fields

        # Fagområde
        if field["fieldName"] == "Fagområde":
            subject_area = transformed_concept.get("fagområde", {})
            text_list = subject_area.get("nb", [])
            text_list.append(field["value"])
            subject_area["nb"] = text_list
            transformed_concept["fagområde"] = subject_area

        # Forkortelse
        if field["fieldName"] == "Forkortelse":
            transformed_concept["abbreviatedLabel"] = field["value"]

        # Forslag til fagområde (internfelt)
        if field["fieldName"] == "Forslag til fagområde":
            internal_fields = transformed_concept.get("interneFelt", {})
            internal_fields["568acb38-485c-445f-a773-caace03a8483"] = {
                "value": field["value"]
            }
            transformed_concept["interneFelt"] = internal_fields

        # FrarådetTerm
        if field["fieldName"] == "Frarådet term":
            unadvisedTerm = transformed_concept.get("frarådetTerm", {})
            unadvisedTerm["nb"] = [
                field["value"]
            ]
            transformed_concept["frarådetTerm"] = unadvisedTerm

        # Forhold til kilde
        if field["fieldName"] == "Forhold til kilde":
            definisjon = transformed_concept.get("definisjon", {})
            kildebeskrivelse = definisjon.get("kildebeskrivelse", {})
            kildebeskrivelse["forholdTilKilde"] = mapkildetype(field["value"])
            definisjon["kildebeskrivelse"] = kildebeskrivelse
            transformed_concept["definisjon"] = definisjon

        # Kilde til definisjon
        if field["fieldName"] == "Kilde til definisjon":
            definisjon = transformed_concept.get("definisjon", {})
            kildebeskrivelse = definisjon.get("kildebeskrivelse", {})
            kilde = kildebeskrivelse.get("kilde", [])
            kilde += geturitekst(getstrings(field["value"]))
            kildebeskrivelse["kilde"] = kilde
            definisjon["kildebeskrivelse"] = kildebeskrivelse
            transformed_concept["definisjon"] = definisjon

        # Kilde til merknad
        if field["fieldName"] == "Kilde til merknad":
            definisjon = transformed_concept.get("definisjon", {})
            kildebeskrivelse = definisjon.get("kildebeskrivelse", {})
            kilde = kildebeskrivelse.get("kilde", [])
            kilde += getmerknadtekst(getstrings(field["value"]))
            kildebeskrivelse["kilde"] = kilde
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

        # Merknad - nynorsk
        if field["fieldName"] == "Merknad - nynorsk":
            merknad = transformed_concept.get("merknad", {})
            merknad["nn"] = [
                field["value"]
            ]
            transformed_concept["merknad"] = merknad

        # Print id to file if concept should be published in publish job
        if field["fieldName"] == "Offentlig tilgjengelig?":
            if len(field["value"]) > 1:
                print(str(concept["key"]) + ": Multiple values in Offentlig tilgjengelig")
            if (concept["status"].upper() == "GODKJENT") and (field["value"][0].upper() == "JA"):
                listObj = openfile(publish_ids) if os.path.isfile(publish_ids) else []
                listObj.append(mongo_id)
                with open(publish_ids, 'w', encoding="utf-8") as publish_file:
                    json.dump(listObj, publish_file, ensure_ascii=False, indent=4)

    return transformed_concept


def getuser(brreg_user):
    for user_id in admin_users:
        user = admin_users[user_id]
        if user["name"] == brreg_user:
            return user
    return None


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


def getmerknadtekst(string_list):
    return [{"tekst": "Kilde til merknad: " + string} for string in string_list]


def getstrings(value):
    if value is not None:
        return value.split(";")
    else:
        return []


def set_status(status):
    if status == "Utkast":
        return "http://publications.europa.eu/resource/authority/concept-status/DRAFT"
    elif status == "Høring":
        return "http://publications.europa.eu/resource/authority/concept-status/CANDIDATE"
    elif status == "Godkjent":
        return "http://publications.europa.eu/resource/authority/concept-status/CURRENT"
    elif status == "Klar til godkjenning":
        return "http://publications.europa.eu/resource/authority/concept-status/WAITING"
    elif status == "Kvalitetssikring":
        return "http://publications.europa.eu/resource/authority/concept-status/CANDIDATE"
    else:
        print("Unknown status: " + str(status))


def convert_date(timestamp):
    if timestamp:
        # Remove milliseconds from timestamp
        datetime_object = datetime.fromtimestamp(timestamp/1000)
        return datetime.strftime(datetime_object, "%Y-%m-%dT%H:%M:%S.000Z")
    else:
        return None


concepts_file = "brreg_concepts.json"
admin_users_file = args.outputdirectory + "transformed_admin_users.json"
admin_users = openfile(admin_users_file)
outputfileName = args.outputdirectory + "transformed_concepts.json"
publish_ids = args.outputdirectory + "publish_ids.json"

# Kodelisteverdi for ekstern_begrepseier - FDK
ekstern_begrepseier = {
    "Arkivverket": "11160",
    "Datatilsynet": "11420",
    "Digitaliseringsdirektoratet": "11162",
    "Direktoratet for e-helse": "11161",
    "Direktoratet for forvaltning og økonomistyring": "11337",
    "Helsedirektoratet": "11163",
    "Kartverket": "11164",
    "KS": "11165",
    "Lotteri- og stiftelsestilsynet": "15104",
    "Lånekassen": "11166",
    "NAV": "11167",
    "Politiet": "11168",
    "Posten Norge": "12600",
    "Skatteetaten": "11169",
    "Språkrådet": "11336",
    "SSB": "11170",
    "UDI": "11171"
}
# Kodelisteverdi for intern_begrepseier - FDK
intern_begrepseier = {
    "Informasjonsteknologi (IT)": "10506",
    "Registerforvaltning (RF)": "10507",
    "IT - Infrastruktur": "10511",
    "IT - Systemutvikling 1": "10901",
    "IT - Systemutvikling 2": "10902",
    "RF - Tinglysning og regnskap": "10911",
    "RF - Registerdrift": "15301",
    "RF - Jus": "15302",
    "RF - Samordning og system": "15303",
    "FU - Registerutvikling": "15305",
    "FU - Datadrevet utvikling": "15306",
    "IT - Styring": "15307",
    "Virksomhetsstyring (VST)": "15310",
    "VST - Plan og styring": "15311",
    "VST - HR": "15312",
    "VST - Fellestjenester": "15313",
    "Enhetsregisteret": "15800",
    "Foretaksregisteret": "15801",
    "Ektepaktregisteret": "15802",
    "Løsøreregisteret": "15803",
    "Regnskapsregisteret": "15804",
    "Register over reelle rettighetshavere": "15900"
}


with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(concepts_file), outfile, ensure_ascii=False, indent=4)
