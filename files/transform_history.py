import json
import argparse
import re
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
        mongo_id = str(uuid.UUID(int=rd.getrandbits(128), version=4))
        transformed_story = {
            "_id": mongo_id,
            "catalogId": "974760673",
            "datetime": convert_date(story["created"]),
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
    global jira_links
    jira_links = set()
    fdk_field = json_field_map.get(item["field"])
    operation = {}
    user_field = ["/opprettetAv", "/tildeltBruker"]
    internal_field = ["/interneFelt"]
    if fdk_field is not None and fdk_field not in user_field:
        # Add
        if item.get("oldDisplayValue") is None and item.get("newDisplayValue") is not None:
            operation["op"] = "add"
            operation["path"] = fdk_field
            operation["value"] = get_operation(item["field"], item.get("newValue"), strip_jira_links(item["newDisplayValue"]))
        # Replace
        if item.get("oldDisplayValue") is not None and item.get("newDisplayValue") is not None:
            operation["op"] = "replace"
            operation["path"] = fdk_field
            operation["value"] = get_operation(item["field"], item.get("newValue"), strip_jira_links(item["newDisplayValue"]))
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
            operation["value"] = strip_jira_links(item["newValue"])
        # Replace
        if item.get("oldValue") is not None and item.get("newValue") is not None:
            operation["op"] = "replace"
            operation["path"] = fdk_field
            operation["value"] = strip_jira_links(["newValue"])
        # Remove
        if item.get("oldValue") is not None and item.get("newValue") is None:
            operation["op"] = "remove"
            operation["path"] = fdk_field
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


def get_operation(field, value, display_value):
    if field in internal_codelists:
        internal_field_key = internal_codelists[field]
        if value in begrepseier or value in ekstern_begrepseier:
            internal_field_value = value
        else:
            internal_field_value = display_value
        return {
            internal_field_key: {
                "value": internal_field_value
            }
        }
    elif field in internal_fields:
        internal_field_key = internal_fields[field]
        return {
            internal_field_key: {
                "value": display_value
            }
        }
    elif field in fagomraade:
        return {
            "fagområdeKoder": [value]
        }
    else:
        return display_value


def strip_jira_links(string):
    global jira_links
    if string is not None and isinstance(string, str):
        jira_links.update(re.findall(r"\[.*?\|(.*?)]", string))
        return re.sub(r"\[(.*?)\|.*?]", r"\1", string)
    elif string is not None and isinstance(string, list):
        for i in range(len(string)):
            string[i] = strip_jira_links(string[i])
        return string
    else:
        return string


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
jira_links = set()
json_field_map = {
    "summary": "/anbefaltTerm/navn/nb",
    "created": "/opprettet",
    "reporter": "/opprettetAv",
    "Offentlig tilgjengelig?": "/erPublisert",
    "status": "/status",
    "assignee": "/assignedUser",
    "Alternativ term": "/tillattTerm/nb",
    "Alternativt term": "/tillattTerm/nb",  # Typo exists in BRREG-comments
    "Begrepseier": "/interneFelt",
    "Ekstern begrepseier": "/interneFelt",
    "Forslag til fagområde": "/interneFelt",
    "Term engelsk": "/anbefaltTerm/navn/en",
    "Term Engelsk": "/anbefaltTerm/navn/en",
    "Term nynorsk": "/anbefaltTerm/navn/nn",
    "Definisjon": "/definisjon/tekst/nb",
    "Definisjon engelsk": "/definisjon/tekst/en",
    "Definisjon Engelsk": "/definisjon/tekst/en",
    "Definisjon nynorsk": "/definisjon/tekst/nn",
    "Eksempel": "/eksempel/nb",
    "Fagområde": "/fagområdeKoder",
    "Forkortelse": "/abbreviatedLabel",
    "Frarådet term": "/frarådetTerm/nb",
    "Forhold til kilde": "/definisjon/kildebeskrivelse/forholdTilKilde",
    "Kilde til definisjon": "/definisjon/kildebeskrivelse/kilde",
    "Kilde til merknad": "/merknad/kildebeskrivelse/kilde",  # Does not exist in FDK, but is used in BRREG-history
    "Kilde til forklaring": "/forklaring/kildebeskrivelse/kilde",  # Does not exist in FDK, but is used in BRREG-history
    "Kilde til kommentar": "/kommentar/kildebeskrivelse/kilde",  # Does not exist in FDK, but is used in BRREG-history
    "Folkelig forklaring": "/folkeligForklaring/tekst/nb",
    "Merknad": "/merknad/nb",
    "Merknad - nynorsk": "/merknad/nn",
    "Godkjent": "/godkjent",  # Does not exist in FDK, but is used in BRREG-history
    "Bruksområde": "/bruksområde",  # Does not exist in FDK, but is used in BRREG-history
    "Forklaring": "/forklaring",  # Does not exist in FDK, but is used in BRREG-history
    "Godkjenner": "/interneFelt",  # Does not exist in FDK, but is used in BRREG-history
    "Godkjennere": "/godkjennere",  # Does not exist in FDK, but is used in BRREG-history, suspected typo
    "Organisatorisk eier": "/organisatoriskEier",  # Does not exist in FDK, but is used in BRREG-history
    "labels": "/labels"  # Does not exist in FDK, but is used in BRREG-history
}
begrepseier = openfile(args.outputdirectory + "transform_history_begrepseier.json")
ekstern_begrepseier = openfile(args.outputdirectory + "transform_history_ekstern_begrepseier.json")
fagomraade = openfile(args.outputdirectory + "transform_history_fagomraade.json")
internal_codelists = openfile(args.outputdirectory + "transform_history_internal_codelists.json")
internal_fields = openfile(args.outputdirectory + "transform_history_internal_fields.json")

with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(brreg_history_file), outfile, ensure_ascii=False, indent=4)
with open(unknown_fields_file, "r") as unsorted_file:
    lines = set(unsorted_file.readlines())
with open(unknown_fields_file, "w", encoding="utf-8") as sorted_file:
    sorted_file.writelines(sorted(lines))
