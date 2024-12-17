import json
from pymongo import MongoClient
import argparse
from datetime import datetime


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


parser = argparse.ArgumentParser()
parser.add_argument('-o',
                    '--outputdirectory',
                    help="the path to the directory of the output files",
                    required=True)
args = parser.parse_args()
connection = MongoClient(
    f"""mongodb://{input("Username: ")}:{input("Password: ")}@localhost:27017/concept-catalogue?authSource=admin&authMechanism=SCRAM-SHA-1""")


def get_confirmed_input(prompt_message, confirmation_message):
    while True:
        user_input = input(prompt_message)
        confirmation = input(f"{confirmation_message} '{user_input}'? (yes/no): ").strip().lower()
        if confirmation in {"yes", "y"}:
            return user_input
        elif confirmation in {"no", "n"}:
            print("Let's try again.")
        else:
            print("Invalid response. Please type 'yes' or 'no'.")


def get_concepts():
    db = connection["concept-catalogue"]
    with open(args.outputdirectory + 'concepts.json', 'w', encoding="utf-8") as outfile:
        json.dump(list(db.begrep.find({"ansvarligVirksomhet._id": org_id})), outfile, cls=DateTimeEncoder, ensure_ascii=False, indent=4)


def get_catalog_admin():
    db = connection["catalogAdminService"]
    with open(args.outputdirectory + 'admin_codelists.json', 'w', encoding="utf-8") as outfile:
        json.dump(list(db.codeLists.find({"catalogId": org_id})), outfile, ensure_ascii=False, indent=4)
    with open(args.outputdirectory + 'admin_design.json', 'w', encoding="utf-8") as outfile:
        json.dump(list(db.design.find({"_id": org_id})), outfile, ensure_ascii=False, indent=4)
    with open(args.outputdirectory + 'admin_editable_fields.json', 'w', encoding="utf-8") as outfile:
        json.dump(list(db.editableFields.find({"_id": org_id})), outfile, ensure_ascii=False, indent=4)
    with open(args.outputdirectory + 'admin_internal_fields.json', 'w', encoding="utf-8") as outfile:
        json.dump(list(db.internalFields.find({"catalogId": org_id})), outfile, ensure_ascii=False, indent=4)
    with open(args.outputdirectory + 'admin_logo.json', 'w', encoding="utf-8") as outfile:
        json.dump(list(db.logo.find({"_id": org_id})), outfile, ensure_ascii=False, indent=4)
    with open(args.outputdirectory + 'admin_users.json', 'w', encoding="utf-8") as outfile:
        json.dump(list(db.users.find({"catalogId": org_id})), outfile, ensure_ascii=False, indent=4)


def get_catalog_history():
    db = connection["catalog-history-service"]
    with open(args.outputdirectory + 'catalog_history.json', 'w', encoding="utf-8") as outfile:
        json.dump(list(db.updates.find({"catalogId": org_id})), outfile, cls=DateTimeEncoder, ensure_ascii=False, indent=4)


org_id = get_confirmed_input(
    "Please enter an organization ID: ",
    "Please verify that the organization ID is correct:"
)

get_concepts()
get_catalog_admin()
get_catalog_history()
