import json
import argparse
import uuid
import random
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()
rd = random.Random()
rd.seed(105)


def transform(c_file):
    comment_file = openfile(c_file)
    transformed_comments = {}

    for concept_id in comment_file:
        if comment_file[concept_id] is not None and len(comment_file[concept_id]) > 1:
            result = transform_comment(comment_file[concept_id], concept_id)
            transformed_comments[concept_id] = result
    return transformed_comments


def transform_comment(comment_string, concept_id):
    mongo_id = str(uuid.UUID(int=rd.getrandbits(128), version=4))
    transformed_comment = {
        "_id": mongo_id,
        "_class": "no.digdir.catalog_comments_service.model.CommentDBO",
        "comment": comment_string,
        "createdDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "orgNumber": "974761076",
        "topicId": concept_id,
        "user": skatt_user
    }
    return transformed_comment


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


skatt_comments_file = args.outputdirectory + "skatt_comments.json"
transformed_comments_file = args.outputdirectory + "transformed_comments.json"

with open("skatt_user.txt", "r") as skatt_user_file:
    skatt_user = skatt_user_file.read()

with open(transformed_comments_file, 'w', encoding="utf-8") as outfile:
    json.dump(transform(skatt_comments_file), outfile, ensure_ascii=False, indent=4)
