import json


def merge(file_1, file_2):
    merged_concepts = {}
    return merged_concepts


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


concepts_file_1 = openfile("JiraGodkjenteBegreper.txt")
concepts_file_2 = openfile("Jsonbegreper.txt")


with open("brreg_concepts.json", 'w', encoding="utf-8") as outfile:
    json.dump(merge(concepts_file_1, concepts_file_2), outfile, ensure_ascii=False, indent=4)
