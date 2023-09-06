import json
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()


def create_id_file():
    admin_users = openfile(admin_users_file)
    comment_users = openfile(comment_users_file)
    concepts = openfile(concepts_file)
    id_file = {
        "admin_users": [],
        "history_users": [],
        "concepts": []
    }

    for key in admin_users:
        id_file["admin_users"].append(key)
    for key in comment_users:
        id_file["comment_users"].append(key)
    for key in concepts:
        id_file["concepts"].append(key)
    return id_file


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


admin_users_file = args.outputdirectory + "transformed_admin_users.json"
comment_users_file = args.outputdirectory + "transformed_comment_users.json"
concepts_file = args.outputdirectory + "transformed_concepts.json"

outputfileName = args.outputdirectory + "id_delete_file.json"


with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(create_id_file(), outfile, ensure_ascii=False, indent=4)
