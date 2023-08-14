import json
import jsonpatch
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
    for history_list in history_file:
        result = transform_change(history_list)
        transformed_history[history_list] = result
    return transformed_history


def transform_change(history_list):
    transformed_changes = []
    for history in history_list:
        mongo_id = str(uuid.uuid4())
        transformed_changes = {
            "_id": mongo_id,
            "catalogId": "974760673",
            "dateTime": convert_date(history["created"]),
            "operations": transform_story(history),
            "person": getuser(history["author"]),
            "resourceId": history
        }
    return transformed_changes


def transform_story(history):
    transformed_operations = []
    for story in history:
        for item in story:
            new_value = item.get("newDisplayValue")
            if new_value is not None:
                patch = jsonpatch.JsonPatch.from_diff(
                    {"fieldType": item["fieldType"],
                     "field": item["fieldType"],
                     "value": item.get("oldDisplayValue")},
                    {"fieldType": item["fieldType"],
                     "field": item["fieldType"],
                     "value": new_value
                     }
                )
                transformed_operations.append(patch)
    return transformed_operations


def getuser(brreg_user):
    for user in comment_users:
        if user["name"] == brreg_user:
            return {
                "id": brreg_user["_id"],
                "email": brreg_user["email"],
                "name": brreg_user["name"]
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


brreg_history_file = "brreg_history.json"
comment_users_file = "transformed_comment_users.json"
comment_users = openfile(comment_users_file)
outputfileName = args.outputdirectory + "transformed_history.json"

with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(brreg_history_file), outfile, ensure_ascii=False, indent=4)
