import json
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()

environment = input("Please enter the name of the environment (staging/demo/prod): ")
match environment:
    case 'staging':
        relation_uri = "https://concept-catalog.staging.fellesdatakatalog.digdir.no/collections/"
    case 'demo':
        relation_uri = "https://concept-catalog.demo.fellesdatakatalog.digdir.no/collections/"
    case 'prod':
        relation_uri = "https://concept-catalog.fellesdatakatalog.digdir.no/collections/"
    case _:
        sys.exit("Invalid environment input")


def transform(aff_file):
    affected_concepts = openfile(aff_file)
    transformed_concepts = {}
    transformed_count = 0
    for affected_concept in affected_concepts:
        result = transform_concept(affected_concepts[affected_concept])
        if result is not None:
            transformed_concepts[affected_concept] = result
            transformed_count += 1
    print("Transformed concepts: " + str(transformed_count))
    return transformed_concepts


def transform_concept(affected_concept):
    internSeeAlso = affected_concept.get("internSeOgså", [])
    internErstattesAv = affected_concept.get("internErstattesAv", [])
    internBegrepsRelasjon = affected_concept.get("internBegrepsRelasjon", [])
    virksomhet = affected_concept["ansvarligVirksomhet"]["_id"]
    transformed_concept = {}

    if internSeeAlso:
        transformed_concept["internSeOgså"] = list(filter(id_is_not_published, internSeeAlso))
        transformed_concept["seOgså"] = transform_relation(internSeeAlso, affected_concept.get("seOgså", []), virksomhet)
    if internErstattesAv:
        transformed_concept["internErstattesAv"] = list(filter(id_is_not_published, internErstattesAv))
        transformed_concept["erstattesAv"] = transform_relation(internErstattesAv, affected_concept.get("erstattesAv", []), virksomhet)
    if internBegrepsRelasjon:
        transformed_concept["internBegrepsRelasjon"] = list(filter(remove_affected_relation_objects, internBegrepsRelasjon))
        transformed_concept["begrepsRelasjon"] = transform_relation_object(internBegrepsRelasjon, affected_concept.get("begrepsRelasjon", []), virksomhet)

    return transformed_concept


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


def id_is_not_published(concept_id):
    if concept_id in published_ids:
        return False
    else:
        return True


def transform_relation(internal, external, virksomhet):
    modified_external = external
    for relation_id in internal:
        if not id_is_not_published(relation_id):
            modified_external.append(create_relation_uri(relation_id, virksomhet))
    return modified_external


def transform_relation_object(internal, external, virksomhet):
    modified_external = external
    for relation in internal:
        relation_id = relation.get("relatertBegrep", [])
        if not id_is_not_published(relation_id):
            modified_relation = relation
            modified_relation["relatertBegrep"] = create_relation_uri(relation_id, virksomhet)
            modified_external.append(modified_relation)
    return modified_external


def create_relation_uri(_id, virksomhet):
    return relation_uri + virksomhet + "/concepts/" + _id


def remove_affected_relation_objects(relation_object):
    relatert_begrep = relation_object.get("relatertBegrep")
    return id_is_not_published(relatert_begrep)


affected_concepts_file = args.outputdirectory + "affected_concepts.json"
published_ids = openfile(args.outputdirectory + "published_concepts.json")
outputfileName = args.outputdirectory + "transformed_concepts.json"


with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(affected_concepts_file), outfile, ensure_ascii=False, indent=4)
