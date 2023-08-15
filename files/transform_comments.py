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
    transformed_comment = {
        "_id": mongo_id,
        "_class": "no.digdir.catalog_comments_service.model.CommentDBO",
        "comment": {
            comment["body"]
        },
        "createdDate": convert_date(comment["created"]),
        "orgNumber": "974760673",
        "topicId": comment,
        "user": getuser(comment["author"])
    }
    return transformed_comment


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


brreg_comments_file = "brreg_comments.json"
comment_users_file = "transformed_comment_users.json"
comment_users = openfile(comment_users_file)
outputfileName = args.outputdirectory + "transformed_comments.json"

with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(brreg_comments_file), outfile, ensure_ascii=False, indent=4)
