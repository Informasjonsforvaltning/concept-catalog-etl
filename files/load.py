import json
from pymongo import MongoClient
import argparse
from datetime import datetime


parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()
connection = MongoClient(
    f"""mongodb://{input("Username: ")}:{input("Password: ")}@localhost:27017/concept-catalogue?authSource=admin&authMechanism=SCRAM-SHA-1""",
    connectTimeoutMS=600000,
    socketTimeoutMS=600000,
    serverSelectionTimeoutMS=600000
)

errorfileName = args.outputdirectory + "load_errors.json"
catalog_history_date_fields = ["datetime"]
concept_date_fields = ["publiseringsTidspunkt", "opprettet", "gyldigFom", "gyldigTom", "endringslogelement.endringstidspunkt"]


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


def convert_date_fields_to_datetime(doc, date_fields):
    for field in date_fields:
        keys = field.split(".")
        current_level = doc
        for key in keys[:-1]:
            if key in current_level and isinstance(current_level[key], dict):
                current_level = current_level[key]
            else:
                current_level = None
                break
        if current_level and keys[-1] in current_level and isinstance(current_level[keys[-1]], str):
            try:
                current_level[keys[-1]] = datetime.fromisoformat(current_level[keys[-1]])
            except ValueError:
                pass
    return doc


def load_concepts(concepts):
    processed_concepts = [
        convert_date_fields_to_datetime(doc, concept_date_fields) for doc in concepts
    ]
    db = connection["concept-catalogue"]
    if len(processed_concepts) > 0:
        print("---\nStarting to load concept-catalog...")
        result = db.begrep.insert_many(processed_concepts)
        print(f"Successfully inserted {len(result.inserted_ids)}/{len(processed_concepts)} concepts.")


def load_catalog_admin():
    db = connection["catalogAdminService"]
    codelists = openfile(args.outputdirectory + "admin_codelists.json")
    designs = openfile(args.outputdirectory + "admin_design.json")
    editable_fields = openfile(args.outputdirectory + "admin_editable_fields.json")
    internal_fields = openfile(args.outputdirectory + "admin_internal_fields.json")
    logo = openfile(args.outputdirectory + "admin_logo.json")
    users = openfile(args.outputdirectory + "admin_users.json")
    print("---\nStarting to load catalog admin...")
    if len(codelists) > 0:
        print("Inserting catalogAdminService.codelists")
        result = db.codeLists.insert_many(codelists)
        print(f"Successfully inserted {len(result.inserted_ids)}/{len(codelists)} codelists.")
    if len(designs) > 0:
        print("Inserting catalogAdminService.design")
        result = db.design.insert_many(designs)
        print(f"Successfully inserted {len(result.inserted_ids)}/{len(designs)} designs.")
    if len(editable_fields) > 0:
        print("Inserting catalogAdminService.editableFields")
        result = db.editableFields.insert_many(editable_fields)
        print(f"Successfully inserted {len(result.inserted_ids)}/{len(editable_fields)} editable fields.")
    if len(internal_fields) > 0:
        print("Inserting catalogAdminService.internalFields")
        result = db.internalFields.insert_many(internal_fields)
        print(f"Successfully inserted {len(result.inserted_ids)}/{len(internal_fields)} internal fields.")
    if len(logo) > 0:
        print("Inserting catalogAdminService.logo")
        result = db.logo.insert_many(logo)
        print(f"Successfully inserted {len(result.inserted_ids)}/{len(logo)} logos.")
    if len(users) > 0:
        print("Inserting catalogAdminService.users")
        result = db.users.insert_many(users)
        print(f"Successfully inserted {len(result.inserted_ids)}/{len(users)} users.")


def load_catalog_history(catalog_history):
    processed_history = [
        convert_date_fields_to_datetime(doc, catalog_history_date_fields) for doc in catalog_history
    ]
    db = connection["catalog-history-service"]
    if len(processed_history) > 0:
        print("---\nStarting to load catalog history...")
        result = db.updates.insert_many(processed_history)
        print(f"Successfully inserted {len(result.inserted_ids)}/{len(processed_history)} updates.")


load_concepts(openfile(args.outputdirectory + "concepts.json"))
load_catalog_admin()
load_catalog_history(openfile(args.outputdirectory + "catalog_history.json"))

print("---\nLoad finished.\nPlease trigger a reindex of concept-catalog.")
