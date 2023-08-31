import json
import argparse
import uuid
import random
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()
rd = random.Random()
rd.seed(10)


def transform(h_file):
    history_file = openfile(h_file)
    transformed_history = {}
    for concept_id in history_file:
        result = transform_change(history_file[concept_id], concept_id)
        transformed_history[concept_id] = result
    return transformed_history


def transform_change(history_list, concept_id):
    transformed_changes = []
    for story in history_list:
        mongo_id = uuid.UUID(int=rd.getrandbits(128), version=4)
        transformed_story = {
            "_id": mongo_id,
            "catalogId": "974760673",
            "dateTime": convert_date(story["created"]),
            "operations": transform_story(story["items"]),
            "person": getuser(story["author"]),
            "resourceId": concept_id
        }
        if len(transformed_story["operations"]) > 0:
            transformed_changes.append(transformed_story)
    return transformed_changes


def transform_story(items):
    transformed_operations = []
    for item in items:
        patch = create_jsonpatch(item)
        if patch:
            transformed_operations.append(patch)
    return transformed_operations


def create_jsonpatch(item):
    fdk_field = json_field_map.get(item["field"])
    operation = {}
    user_field = ["/opprettetAv", "/tildeltBruker"]
    internal_field = ["/interneFelt"]
    if fdk_field is not None and fdk_field not in user_field and fdk_field not in internal_field:
        # Add
        if item.get("oldDisplayValue") is None and item.get("newDisplayValue") is not None:
            operation["op"] = "add"
            operation["path"] = fdk_field
            operation["value"] = item["newDisplayValue"]
        # Replace
        if item.get("oldDisplayValue") is not None and item.get("newDisplayValue") is not None:
            operation["op"] = "replace"
            operation["path"] = fdk_field
            operation["value"] = item["newDisplayValue"]
        # Remove
        if item.get("oldDisplayValue") is not None and item.get("newDisplayValue") is None:
            operation["op"] = "remove"
            operation["path"] = fdk_field
    elif fdk_field is not None and fdk_field not in internal_field and fdk_field in user_field:
        # For users, we are interested in the newValue-field
        # Add
        if item.get("oldValue") is None and item.get("newValue") is not None:
            operation["op"] = "add"
            operation["path"] = fdk_field
            operation["value"] = item["newValue"]
        # Replace
        if item.get("oldValue") is not None and item.get("newValue") is not None:
            operation["op"] = "replace"
            operation["path"] = fdk_field
            operation["value"] = item["newValue"]
        # Remove
        if item.get("oldValue") is not None and item.get("newValue") is None:
            operation["op"] = "remove"
            operation["path"] = fdk_field
    elif fdk_field is not None and fdk_field in internal_field:
        # For internal fields/codelists, we need to set the value a bit differently
        if item["field"] in internal_codelists:
            # Add
            if item.get("oldDisplayValue") is None and item.get("newDisplayValue") is not None:
                operation["op"] = "add"
                operation["path"] = fdk_field
                operation["value"] = {
                    internal_codelists[item["field"]]: {
                        # TODO: Sjekk om finnes i codelist, hvis ikke legg inn displayvalue
                        # "value": begrepseier[]
                    }
                }
    else:
        with open(unknown_fields_file, "a") as myfile:
            myfile.write(item["field"] + "\n")
    return operation


def getuser(brreg_user):
    for user_id in comment_users:
        user = comment_users[user_id]
        if user["name"] == brreg_user:
            return {
                "id": user["_id"],
                "email": user["email"],
                "name": user["name"]
            }
    return None


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


def convert_date(timestamp):
    if timestamp:
        # Remove milliseconds from timestamp
        datetime_object = datetime.fromtimestamp(timestamp/1000)
        return datetime.strftime(datetime_object, "%Y-%m-%dT%H:%M:%S.000Z")
    else:
        return None


brreg_history_file = args.outputdirectory + "brreg_history.json"
comment_users_file = args.outputdirectory + "transformed_comment_users.json"
comment_users = openfile(comment_users_file)
outputfileName = args.outputdirectory + "transformed_history.json"
unknown_fields_file = args.outputdirectory + "unknown_fields.txt"
json_field_map = {
    "summary": "/anbefaltTerm/navn/nb",
    "created": "/opprettet",
    "reporter": "/opprettetAv",
    "Offentlig tilgjengelig": "/erPublisert",
    "status": "/status",
    "assignee": "/tildeltBruker",
    "Alternativ term": "/tillattTerm/nb",
    "Begrepseier": "/interneFelt",
    "Ekstern begrepseier": "/interneFelt",
    "Forslag til fagområde": "/interneFelt",
    "Term engelsk": "/anbefaltTerm/navn/en",
    "Term nynorsk": "/anbefaltTerm/navn/nn",
    "Definisjon": "/definisjon/tekst/nb",
    "Definisjon engelsk": "/definisjon/tekst/en",
    "Definisjon nynorsk": "/definisjon/tekst/nn",
    "Eksempel": "/eksempel/nb",
    "Fagområde": "/fagområde/nb",
    "Frarådet term": "/frarådetTerm/nb",
    "Forhold til kilde": "/definisjon/kildebeskrivelse/forholdTilKilde",
    "Kilde til definisjon": "/definisjon/kildebeskrivelse/kilde",
    "Folkelig forklaring": "/folkeligForklaring/tekst/nb",
    "Merknad": "/merknad/nb"
}
begrepseier = {
    "Ektepaktregisteret": 0,
    "Enhetsregisteret": 1,
    "Foretaksregisteret": 2,
    "FU - Datadrevet utvikling": 3,
    "FU - Registerutvikling": 4,
    "Informasjonsteknologi (IT)": 5,
    "IT - Infrastruktur": 6,
    "IT - Styring": 7,
    "IT - Systemutvikling 1": 8,
    "IT - Systemutvikling 2": 9,
    "Løsøreregisteret": 10,
    "Register over reelle rettighetshavere": 11,
    "Registerforvaltning (RF)": 12,
    "Regnskapsregisteret": 13,
    "RF - Jus": 14,
    "RF - Registerdrift": 15,
    "RF - Samordning og system": 16,
    "RF - Tinglysning og regnskap": 17,
    "Virksomhetsstyring (VST)": 18,
    "VST - Fellestjenester": 19,
    "VST - HR": 20,
    "VST - Plan og styring": 21
}
ekstern_begrepseier = {
    "11160": "Arkivverket",
    "11420": "Datatilsynet",
    "11162": "Digitaliseringsdirektoratet",
    "11161": "Direktoratet for e-helse",
    "11337": "Direktøratet for forvaltning og økonomistyring",
    "11163": "Helsedirektoratet",
    "11164": "Kartverket",
    "11165": "KS",
    "15104": "Lotteri- og stiftelsestilsynet",
    "11166": "Lånekassen",
    "11167": "NAV",
    "11168": "Politiet",
    "12600": "Posten Norge",
    "11169": "Skatteetaten",
    "11336": "Språkrådet",
    "11170": "SSB",
    "11171": "UDI"
}

internal_codelists = {
    "Begrepseier": "c707276d-2f2e-4c13-b6a6-f066878d594b",
    "Ekstern begrepseier": "0da72785-ede5-49ab-b2de-20f7790320f0"
}

internal_fields = {
    "Forslag til fagområde": "568acb38-485c-445f-a773-caace03a8483"
}


with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(brreg_history_file), outfile, ensure_ascii=False, indent=4)
with open(unknown_fields_file, "r") as unsorted_file:
    lines = set(unsorted_file.readlines())
with open(unknown_fields_file, "w", encoding="utf-8") as sorted_file:
    sorted_file.writelines(sorted(lines))
