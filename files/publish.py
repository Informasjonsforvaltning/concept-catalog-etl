import json
import requests


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


publish_list = openfile("publish_ids.json")


with open("publish_results.json", 'w', encoding="utf-8") as outfile:
    json.dump(publish(publish_list), outfile, ensure_ascii=False, indent=4)
