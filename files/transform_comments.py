import json
import argparse
import uuid
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()
namespace = uuid.uuid4()


def transform(c_file):
    comment_file = openfile(c_file)
    transformed_comments = {}

    for comment in comment_file:
        result = transform_comment(comment)
        transformed_comments[result.get("_id")] = result

    return transformed_comments


def transform_comment(comment):
    mongo_id = str(uuid.uuid4())
    transformed_concept = {
        "_id": mongo_id,
        "_class": "no.fdk.concept_catalog.model.Begrep",
        "ansvarligVirksomhet": {
            "_id": "974760673"
        },
        "anbefaltTerm": {
            "navn": {
                "nb": concept["summary"]
            }
        },
        "erPublisert": "false",
        "bruksområde": {},
        "versjonsnr": {
            "major": 0,
            "minor": 0,
            "patch": 1
        },
        "opprettet": convert_date(concept["created"]),
        "opprettetAv": concept["reporter"],
        "originaltBegrep": mongo_id,
        "status": setstatus(concept.get("status")),
        "kontaktpunkt": {
            "harEpost": "informasjonsforvaltning@brreg.no",
            "harTelefon": "+47 75007500"
        }
        # ,
        # TODO: Kommenter inn når klar
        # "tildeltBruker": getuser(concept["assignee"])
    }
    if len(concept["history"]) > 0:
        transformed_concept["endringslogelement"] = {
            "endretAv":
                getuser(concept["history"][-1]["author"])["name"],
            "endringstidspunkt":
                convert_date(concept["history"][-1]["created"])
        }
    else:
        transformed_concept["endringslogelement"] = {
            "endretAv":
                getuser(concept["history"][-1]["author"])["name"],
            "endringstidspunkt":
                convert_date(concept["created"])
        }

    for field in concept["customFieldValues"]:
        # Tillatt term


    return transformed_concept


def getuser(brreg_user):
    # TODO: Åpne brukerfil og populer liste på starten, hent bruker i denne metoden
    return

def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)

def getstrings(value):
    if value is not None:
        return value.split(";")
    else:
        return []


def convert_date(timestamp):
    if timestamp:
        # Remove milliseconds from timestamp
        datetime_object = datetime.fromtimestamp(timestamp/1000)
        return datetime.strftime(datetime_object, "%Y-%m-%dT%H:%M:%S.000Z")
    else:
        return None


brreg_comments_file = "brreg_comments.json"
brreg_users_file = "brreg_users.json"
brreg_users = openfile(brreg_users_file)
outputfileName = args.outputdirectory + "transformed_comments.json"

with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(brreg_comments_file), outfile, ensure_ascii=False, indent=4)
