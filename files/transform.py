import json
import argparse
import re


parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()

utkast = 0
kandidat= 0
gjeldende = 0
til_godkjenning = 0
foreldet = 0
ukjent = 0

def get_correct_version(status_uri):
    global utkast
    global kandidat
    global gjeldende
    global til_godkjenning
    global foreldet
    global ukjent
    if status_uri == 'http://publications.europa.eu/resource/authority/concept-status/DRAFT':
        utkast += 1
        return {
            "major": 0,
            "minor": 1,
            "patch": 0
        }
    elif status_uri == 'http://publications.europa.eu/resource/authority/concept-status/CANDIDATE':
        kandidat += 1
        return {
            "major": 0,
            "minor": 5,
            "patch": 0
        }
    elif status_uri == 'http://publications.europa.eu/resource/authority/concept-status/CURRENT':
        gjeldende += 1
        return {
            "major": 1,
            "minor": 0,
            "patch": 0
        }
    elif status_uri == 'http://publications.europa.eu/resource/authority/concept-status/WAITING':
        til_godkjenning += 1
        return {
            "major": 0,
            "minor": 8,
            "patch": 0
        }
    elif status_uri == 'http://publications.europa.eu/resource/authority/concept-status/RETIRED':
        foreldet += 1
        return {
            "major": 2,
            "minor": 0,
            "patch": 0
        }
    else:
        ukjent += 1
        print(status_uri)
        return None


def transform(c_file):
    concepts = openfile(c_file)
    transformed_concepts = {}
    transformed_count = 0
    for concept in concepts:
        result = transform_concept(concept, concepts[concept])
        if result:
            transformed_concepts[concept] = result
            transformed_count += 1
    print("Total number of transformed concepts: " + str(transformed_count))
    return transformed_concepts


def transform_concept(_id, concept):
    transformed_concept = {}
    version = get_correct_version(concept["statusURI"])
    if version is not None:
        transformed_concept["versjonsnr"] = version
        return transformed_concept
    else:
        return None


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


outputfileName = args.outputdirectory + "transformed_concepts.json"
concepts_file = args.outputdirectory + "extracted_concepts.json"

with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(concepts_file), outfile, ensure_ascii=False, indent=4)
print("Utkast: " + str(utkast))
print("Kandidat: " + str(kandidat))
print("Gjeldende: " + str(gjeldende))
print("Til godkjenning: " + str(til_godkjenning))
print("Foreldet: " + str(foreldet))
print("Ukjent : " + str(ukjent))
