import json

from pymongo import MongoClient
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-o',
                    '--outputdirectory',
                    help="the path to the directory of the output files",
                    required=True)
args = parser.parse_args()
connection = MongoClient(
    f"""mongodb://{input("Username: ")}:{input("Password: ")}@localhost:27017/concept-catalogue?authSource=admin&authMechanism=SCRAM-SHA-1""")


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


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


def delete_concepts():
    db = connection["concept-catalogue"]
    print("Deleting concepts...")
    result = db.begrep.delete_many({"ansvarligVirksomhet._id": org_id})
    print(f"Successfully deleted {result.deleted_count} concepts")


def delete_catalog_admin():
    db = connection["catalogAdminService"]
    # Code lists:
    print("Deleting catalogAdminService.codelists...")
    result = db.codeLists.delete_many({"catalogId": org_id})
    print(f"Successfully deleted {result.deleted_count} codelists")
    # Design:
    print("Deleting catalogAdminService.design...")
    result = db.design.delete_many({"_id": org_id})
    print(f"Successfully deleted {result.deleted_count} designs")
    # Editable fields:
    print("Deleting catalogAdminService.editableFields...")
    result = db.editableFields.delete_many({"_id": org_id})
    print(f"Successfully deleted {result.deleted_count} editable fields")
    # Internal fields:
    print("Deleting catalogAdminService.internalFields...")
    result = db.internalFields.delete_many({"catalogId": org_id})
    print(f"Successfully deleted {result.deleted_count} internal fields")
    # Logo:
    print("Deleting catalogAdminService.logo...")
    db.logo.delete_many({"_id": org_id})
    print(f"Successfully deleted {result.deleted_count} logos")
    # Users:
    print("Deleting catalogAdminService.users...")
    result = db.users.delete_many({"catalogId": org_id})
    print(f"Successfully deleted {result.deleted_count} users")


def delete_catalog_history():
    db = connection["catalog-history-service"]
    print("Deleting catalog-history-service...")
    result = db.updates.delete_many({"catalogId": org_id})
    print(f"Successfully deleted {result.deleted_count} catalog histories")


def delete_turtle(metas):
    ids_to_delete = []
    print("---\nConverting conceptMeta fdkIds to turtle IDs")
    for meta in metas:
        ids_to_delete.append("concept-" + meta["fdkId"])
        ids_to_delete.append("concept-no-records-" + meta["fdkId"])
    db = connection["conceptHarvester"]
    print("---\nDeleting turtle...")
    result = db.turtle.delete_many({"_id": {"$in": ids_to_delete}})
    print(f"Successfully deleted {result.deleted_count}/{len(ids_to_delete)} turtle docs")


def delete_concept_meta(metas):
    ids_to_delete = [doc["_id"] for doc in metas]
    db = connection["conceptHarvester"]
    print("---\nDeleting conceptMeta...")
    result = db.conceptMeta.delete_many({"_id": {"$in": ids_to_delete}})
    print(f"Successfully deleted {result.deleted_count}/{len(ids_to_delete)} conceptMeta docs")


def get_harvester_concept_meta():
    db = connection["conceptHarvester"]
    with open(args.outputdirectory + 'concept_meta.json', 'w', encoding="utf-8") as outfile:
        json.dump(list(db.conceptMeta.find({"_id": {"$regex": org_id}})), outfile, ensure_ascii=False, indent=4)


org_id = get_confirmed_input(
    "Please enter an organization ID: ",
    "Please verify that the organization ID is correct:"
)
delete_concepts()
delete_catalog_admin()
delete_catalog_history()
get_harvester_concept_meta()
print("Finished deleting, now manually initiate harvest of the emptied catalog, and return to this window when done.")
get_confirmed_input("Please confirm that you've finished harvesting: ",
                    "Please repeat your answer: ")
concept_meta = openfile(args.outputdirectory + "concept_meta.json")
delete_turtle(concept_meta)
delete_concept_meta(concept_meta)
