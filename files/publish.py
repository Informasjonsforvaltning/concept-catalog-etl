import json
import requests
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()


def publish(concepts_to_be_published):
    publish_result = {}
    for concept in concepts_to_be_published:
        _id = concept["_id"]
        r = requests.post(f"http://concept-catalog:8080/begreper/{_id}/publish")
        publish_result[concept] = r.status_code
    return publish_result


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


publish_ids_file = args.outputdirectory + "publish_ids.json"
publish_list = openfile(publish_ids_file)


with open("publish_results.json", 'w', encoding="utf-8") as outfile:
    json.dump(publish(publish_list), outfile, ensure_ascii=False, indent=4)
