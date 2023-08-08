import json
import argparse
import uuid

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()


def transform(u_file):
    usr_file = openfile(u_file)
    transformed_users = {}

    projects = usr_file["projects"]
    project = next(prj for prj in projects if prj["name"] == "BEGREP")
    users = project["users"]
    for user in users:
        result = transform_user(user)
        transformed_users[result.get("_id")] = result
    return transformed_users


def transform_user(user):
    mongo_id = str(uuid.uuid4())
    transformed_user = {
        "_id": mongo_id,
        "_class": "no.digdir.catalog_comments_service.model.UserDBO",
        "email": user["email"],
        "name": user["name"]
    }
    return transformed_user


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


input_file = "brreg_concepts.json"
outputfileName = args.outputdirectory + "transformed_users.json"

with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(input_file), outfile, ensure_ascii=False, indent=4)