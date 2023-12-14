import json
import argparse
import uuid
import random

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()
rd = random.Random()
rd.seed(15)


def transform(u_file, usertype):
    usr_file = openfile(u_file)
    transformed_users = {}

    projects = usr_file["projects"]
    project = next(prj for prj in projects if prj["name"] == "BEGREP")
    users = project["users"]
    for user in users:
        mongo_id = str(uuid.UUID(int=rd.getrandbits(128), version=4))
        result = transform_user(user, usertype, mongo_id)
        transformed_users[mongo_id] = result

    return transformed_users


def transform_user(user, usertype, mongo_id):
    transformed_user = {}
    if usertype == "comment":
        transformed_user = {
            "_id": mongo_id,
            "_class": "no.digdir.catalog_comments_service.model.UserDBO",
            "email": user["email"] if user.get("email") is not None else "",
            "name": user["name"]
        }
    elif usertype == "admin":
        transformed_user = {
            "_id": mongo_id,
            "_class": "no.digdir.catalog_admin_service.model.User",
            "catalogId": "974760673",
            "email": user["email"] if user.get("email") is not None else "",
            "name": user["name"]
        }
    return transformed_user


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


input_file = "brreg_concepts.json"
comment_outputfileName = args.outputdirectory + "transformed_comment_users.json"
admin_outputfileName = args.outputdirectory + "transformed_admin_users.json"

with open(comment_outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(input_file, "comment"), outfile, ensure_ascii=False, indent=4)

with open(admin_outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(input_file, "admin"), outfile, ensure_ascii=False, indent=4)