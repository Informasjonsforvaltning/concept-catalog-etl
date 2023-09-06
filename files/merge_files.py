import json


def merge(file_1, file_2):
    first_set = set(file_1["projects"])
    second_set = set(file_2["projects"])
    return first_set.union(second_set)


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


concepts_file_1 = openfile("JiraGodkjenteBegreper.json")
concepts_file_2 = openfile("Jsonbegreper.json")


with open("brreg_concepts.json", 'w', encoding="utf-8") as outfile:
    json.dump(merge(concepts_file_1, concepts_file_2), outfile, ensure_ascii=False, indent=4)
