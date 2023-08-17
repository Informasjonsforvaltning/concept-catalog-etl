import json
import argparse
import uuid
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()
namespace = uuid.uuid4()


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
        mongo_id = str(uuid.uuid4())
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
    if fdk_field is not None and fdk_field not in user_field:
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
    elif fdk_field is not None and fdk_field in user_field:
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
    "Term engelsk": "/anbefaltTerm/navn/en",
    "Term nynorsk": "/anbefaltTerm/navn/nn",
    "Definisjon": "/definisjon/tekst/nb",
    "Definisjon engelsk": "/definisjon/tekst/en",
    "Definisjon nynorsk": "/definisjon/tekst/nn",
    "Eksempel": "/eksempel/nb",
    "Fagområde": "/fagområde/nb",
    #  TODO: "Bruksområde inn i fagområde"
    "Frarådet term": "/frarådetTerm/nb",
    "Forhold til kilde": "/definisjon/kildebeskrivelse/forholdTilKilde",
    "Kilde til definisjon": "/definisjon/kildebeskrivelse/kilde",
    "Folkelig forklaring": "/folkeligForklaring/tekst/nb",
    "Merknad": "/merknad/nb"
}

with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(brreg_history_file), outfile, ensure_ascii=False, indent=4)
with open(unknown_fields_file, "r") as unsorted_file:
    lines = set(unsorted_file.readlines())
with open(unknown_fields_file, "w", encoding="utf-8") as sorted_file:
    sorted_file.writelines(sorted(lines))
