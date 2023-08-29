import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()


def transform(c_file):
    concepts = openfile(c_file)
    transformed_concepts = {}

    for key in concepts:
        concept = concepts[key]
        status_uri = set_status(concept, get_highest_published_version(concepts, concept["originaltBegrep"]))
        transformed_concept = {
            "statusURI": status_uri
        }
        print(concept)
        print(transformed_concept)
        transformed_concepts[key] = transformed_concept

    return transformed_concepts


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


def get_highest_published_version(concepts, originalId):
    highest_version = {"major": 0, "minor": 0, "patch": 1}
    for key in concepts:
        concept = concepts[key]
        if concept["originaltBegrep"] == originalId and compare_semver(concept["versjonsnr"], highest_version) and bool(concept["erPublisert"]):
            highest_version = concept["versjonsnr"]
    return highest_version


def compare_semver(sv_1, sv_2):
    if sv_1["major"] > sv_2["major"]:
        return True
    elif sv_1["major"] < sv_2["major"]:
        return False
    elif sv_1["minor"] > sv_2["minor"]:
        return True
    elif sv_1["minor"] < sv_2["minor"]:
        return False
    else:
        return sv_1["patch"] >= sv_2["patch"]


def set_status(concept, highest_published_version):
    if concept["status"] == "UTKAST":
        return "http://publications.europa.eu/resource/authority/concept-status/DRAFT"
    elif concept["status"] == "HOERING":
        return "http://publications.europa.eu/resource/authority/concept-status/CANDIDATE"
    elif concept["status"] == "GODKJENT" or concept["status"] == "PUBLISERT":
        if not bool(concept["erPublisert"]):
            return "http://publications.europa.eu/resource/authority/concept-status/CURRENT"
        elif compare_semver(highest_published_version, concept["versjonsnr"]):
            return "http://publications.europa.eu/resource/authority/concept-status/DEPRECATED"
        else:
            return "http://publications.europa.eu/resource/authority/concept-status/CURRENT"
    else:
        print("Unknown status: " + concept["status"])


concepts_file = args.outputdirectory + "mongo_concepts.json"
outputfileName = args.outputdirectory + "transformed_concepts.json"

with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(concepts_file), outfile, ensure_ascii=False, indent=4)
