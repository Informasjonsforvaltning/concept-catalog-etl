import json
import argparse
import uuid
import random
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()
rd = random.Random()
rd.seed(5)


def transform(c_file):
    comment_file = openfile(c_file)
    transformed_comments = {}

    for concept_id in comment_file:
        result = transform_comment(comment_file[concept_id], concept_id)
        transformed_comments[concept_id] = result
    return transformed_comments


def transform_comment(comment_list, concept_id):
    transformed_comments = []
    for comment in comment_list:
        mongo_id = uuid.UUID(int=rd.getrandbits(128), version=4)
        transformed_comment = {
            "_id": mongo_id,
            "_class": "no.digdir.catalog_comments_service.model.CommentDBO",
            "comment": comment["body"],
            "createdDate": convert_date(comment["created"]),
            "orgNumber": "974760673",
            "topicId": concept_id,
            "user": getuser(comment["author"])
        }
        transformed_comments.append(transformed_comment)
    return transformed_comments


def getuser(brreg_user):
    for user_id in comment_users:
        user = comment_users[user_id]
        if user["name"] == brreg_user:
            return user["_id"]
    return None


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


brreg_comments_file = args.outputdirectory + "brreg_comments.json"
comment_users_file = args.outputdirectory + "transformed_comment_users.json"
comment_users = openfile(comment_users_file)
outputfileName = args.outputdirectory + "transformed_comments.json"

with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(brreg_comments_file), outfile, ensure_ascii=False, indent=4)
