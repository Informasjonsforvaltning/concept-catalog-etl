import json
import argparse
import datetime
import os

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()


def transform(c_file):
    concepts = openfile(c_file)
    transformed_concepts = {}
    transformed_count = 0
    for concept in concepts:
        result = transform_concept(concept)
        transformed_concepts[result.get("_id")] = result
        transformed_count += 1
    print("Total number of transformed concepts: " + str(transformed_count))
    return transformed_concepts


def transform_concept(concept):
    transformed_concept = {
        "_id": concept["term"].get("identifier"),
        "_class": "no.fdk.concept_catalog.model.BegrepDBO",
        "ansvarligVirksomhet": {
            "_id": "974761076"
        },
        "anbefaltTerm": {
            "navn": {
                "nb": concept["term"]
                .get("properties")
                .get("http://purl.org/dc/elements/1.1/title")
                .get("value"),
                "en": concept["term"]
                .get("localisedProperties")
                .get("http://purl.org/dc/elements/1.1/title", {})
                .get("English (United Kingdom)", {})
                .get("value"),
                "nn": concept["term"]
                .get("localisedProperties")
                .get("http://purl.org/dc/elements/1.1/title", {})
                .get("Norwegian Nynorsk", {}).get("value"),
            }
        },
        "definisjon": {
            "tekst": {
                "nb": concept["term"]
                .get("properties")
                .get("http://purl.org/dc/elements/1.1/description", {})
                .get("value")
            },
            "kildebeskrivelse": {
                "forholdTilKilde":
                    mapkildetype(
                        concept["term"]
                        .get("properties")
                        .get("http://www.skatteetaten.no/schema/properties/sourceType", {})
                        .get("value"),
                        concept["term"].get("identifier")
                    ),
                "kilde": [{
                    "uri":
                        concept["term"]
                        .get("properties")
                        .get("http://www.skatteetaten.no/schema/properties/urlSourceOfDefinition", {})
                        .get("value"),
                    "tekst":
                        concept["term"]
                        .get("properties")
                        .get("http://www.skatteetaten.no/schema/properties/sourceOfDefinition", {})
                        .get("value")
                    }]
            }
        },
        "eksempel": {
            "nb": getstrings(
                concept["term"]
                .get("properties")
                .get("http://www.w3.org/2004/02/skos/core#example", {})
                .get("value")
            )
        },
        "endringslogelement": {
            "endretAv":
                concept["term"]
                .get("properties")
                .get("http://www.skatteetaten.no/schema/properties/lastUpdatedBy")
                .get("value"),
            "endringstidspunkt":
                convert_date(
                    concept["term"]
                    .get("properties")
                    .get("http://www.skatteetaten.no/schema/properties/lastUpdated")
                    .get("value")
                )
        },
        "erPublisert": "false",
        "fagområdeKoder": get_fagomraade(concept["term"]["vocabIdentifier"]),
        "definisjonForAllmennheten": {
            "tekst": {
                "nb":
                    concept["term"]
                    .get("properties")
                    .get("http://www.skatteetaten.no/schema/properties/popularExplanation")
                    .get("value")
            },
            "kildebeskrivelse": {
                "kilde": [{
                    "tekst":
                        concept["term"]
                        .get("properties")
                        .get("http://www.skatteetaten.no/schema/properties/sourceForPopularExplanation", {})
                        .get("value")
                }]
            }
        },
        "frarådetTerm": {
            "nb": getstrings(
                concept["term"]
                .get("properties")
                .get("http://www.w3.org/2004/02/skos/core#hiddenLabel", {})
                .get("value")
            )
        },
        "interneFelt": {
            # Ansvarlig organisatorisk enhet
            "337872c1-36e8-4d2c-a52c-bef0c0437b58": {
                "value": concept["term"]
                .get("properties")
                .get("http://www.skatteetaten.no/schema/properties/responsibleOrganisationalUnit", {})
                .get("value")
            },
            # Beslutningskommentar
            "7280610b-0fcd-4ec3-8da7-c7ad32fd76dc": {
                "value": concept["term"]
                .get("properties")
                .get("http://www.w3.org/2004/02/skos/core#changeNote", {})
                .get("value")
            },
            # Egenskapsnavn
            "cd68dbc3-eea4-4a47-bd1d-c0d7650222f8": {
                "value": convert_bool(
                    concept["term"]
                    .get("properties")
                    .get("http://www.skatteetaten.no/schema/properties/propertyName", {})
                    .get("value")
                )
            },
            # Forretningsbegrep
            "76fed193-c34d-469f-b38d-6a236f247fcc": {
                "value": convert_bool(
                    concept["term"]
                    .get("properties")
                    .get("http://www.skatteetaten.no/schema/properties/businessConcept", {})
                    .get("value")
                )
            },
            # Forvaltningsmerknad
            "ea21bbec-a262-4223-b234-09045c499098": {
                "value": concept["term"]
                .get("properties")
                .get("http://www.skatteetaten.no/schema/properties/forvaltningsmerknad", {})
                .get("value")
            },
            # Teknisk begrepsnavn
            "5dc1d0ba-1638-4ed8-b5b4-ea4fa43df5d3": {
                "value": concept["term"]
                .get("properties")
                .get("http://www.skatteetaten.no/schema/properties/tekniskTerm", {})
                .get("value")
            }
        },
        "merknad": {
            "nb":
                concept["term"]
                .get("properties")
                .get("http://www.skatteetaten.no/schema/properties/conceptNote", {})
                .get("value")
        },
        "originaltBegrep": concept["term"].get("identifier"),
        "statusURI": set_status_uri(
            concept["term"]
            .get("properties")
            .get("http://www.skatteetaten.no/schema/properties/conceptstatus", {})
            .get("value")
        ),
        "tillattTerm": {
            "nb": getstrings(
                    concept["term"]
                    .get("properties")
                    .get("http://www.w3.org/2004/02/skos/core#altLabel", {})
                    .get("value")
            )
        },
        "versjonsnr": {
            "major": 0,
            "minor": 0,
            "patch": 1
        },
        "gyldigFom":
            convert_date(
                concept["term"]
                .get("properties")
                .get("http://www.skatteetaten.no/schema/properties/validFrom", {})
                .get("value")
            ),
        "gyldigTom":
            convert_date(
                concept["term"]
                .get("properties")
                .get("http://www.skatteetaten.no/schema/properties/validTo", {})
                .get("value")
            )
    }
    if (concept["term"].get("properties").get("http://www.skatteetaten.no/schema/properties/nonPublic", {}).get("value").lower()) == "nei":
        listObj = openfile(publish_ids) if os.path.isfile(publish_ids) else []
        listObj.append(concept["term"].get("identifier"))
        with open(publish_ids, 'w', encoding="utf-8") as publish_file:
            json.dump(listObj, publish_file, ensure_ascii=False, indent=4)

    return remove_empty_from_dict(transformed_concept)


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


def remove_empty_from_dict(d):
    if type(d) is dict:
        new_dict = {}
        for k, v in d.items():
            tmp_v = remove_empty_from_dict(v)
            if should_keep_value(tmp_v):
                new_dict[k] = tmp_v
        if len(new_dict) > 0:
            return new_dict
    elif type(d) is list:
        new_list = []
        for v in d:
            tmp_v = remove_empty_from_dict(v)
            if should_keep_value(tmp_v):
                new_list.append(tmp_v)
        if len(new_list) > 0:
            return new_list
    else:
        return d


def should_keep_value(value):
    if type(value) is dict or type(value) is list:
        return len(value) > 0
    else:
        return value is not None


def convert_bool(string_value):
    if string_value:
        if string_value.lower() == "ja":
            return "true"
        elif string_value.lower() == "nei":
            return "false"
        else:
            print("Warning - Expected boolean value is not ja/nei: " + string_value)
            print("Returning noneValue")
            return None
    else:
        return string_value


def get_fagomraade(guid):
    if guid in fagomraader:
        return [str(fagomraader[guid])]
    else:
        return []


def getstrings(value):
    if value is not None:
        return value.split(";")
    else:
        return []


def mapkildetype(kildetype, begrep_id):
    if kildetype == "sitat fra kilde":
        return "SITATFRAKILDE"
    elif kildetype == "basert på kilde":
        return "BASERTPAAKILDE"
    elif kildetype == "egendefinert":
        return "EGENDEFINERT"
    else:
        print("Unknown kildetype: " + str(kildetype) + " for begrep: " + str(begrep_id))
        return None


def set_status_uri(status):
    if status == "Utkast":
        return "http://publications.europa.eu/resource/authority/concept-status/DRAFT"
    elif status == "Registrert":
        return "http://publications.europa.eu/resource/authority/concept-status/DRAFT"
    elif status == "Høring":
        return "http://publications.europa.eu/resource/authority/concept-status/CANDIDATE"
    elif status == "Godkjent":
        return "http://publications.europa.eu/resource/authority/concept-status/CURRENT"
    elif status == "Klar til godkjenning":
        return "http://publications.europa.eu/resource/authority/concept-status/WAITING"
    elif status == "Kvalitetssikring":
        return "http://publications.europa.eu/resource/authority/concept-status/CANDIDATE"
    elif status == "Kvalifisert - formell og innholdsmessig korrekt":
        return "http://publications.europa.eu/resource/authority/concept-status/CANDIDATE"
    elif status == "Tilbaketrukket":
        return "http://publications.europa.eu/resource/authority/concept-status/RETIRED"
    else:
        print("Unknown status: " + str(status))


def convert_date(dateobject):
    if dateobject:
        return datetime.datetime.strftime(
                datetime.datetime.strptime(dateobject, '%Y-%m-%d'),
                "%Y-%m-%dT%H:%M:%S.000Z")
    else:
        return None


concepts_file = "skatt_concepts.json"
fagomraader = {
    "140ba167-a9e6-d840-a421-870ded2c2bd9": "0",
    "2172b8e1-3a0a-11e7-b2d6-0050568204d6": "1",
    "ed59db73-4a7f-3e4c-a3fa-8af2bc619656": "2",
    "f4ecef00-516d-c547-8680-92913322ff2b": "3",
    "08faed06-d836-e948-8d62-73b940a91772": "4",
    "40a53949-1daa-e149-9323-1f725250606b": "5",
    "4eb14457-4594-3445-b5af-ec84ce81aa81": "6",
    "6ba87dd5-75fd-0949-96fa-b9ca6e16d300": "7",
    "029e3ef1-3a1c-11e7-9c64-0050568204d6": "8",
    "20b2e0c1-9fe1-11e5-a9f8-e4115b280940": "9",
    "20b2e0db-9fe1-11e5-a9f8-e4115b280940": "10",
    "20b2e0e6-9fe1-11e5-a9f8-e4115b280940": "11",
    "20b2e0de-9fe1-11e5-a9f8-e4115b280940": "12",
    "20b2e0df-9fe1-11e5-a9f8-e4115b280940": "13",
    "20b2e0e0-9fe1-11e5-a9f8-e4115b280940": "14",
    "20b2e0e1-9fe1-11e5-a9f8-e4115b280940": "15",
    "20b2e0e2-9fe1-11e5-a9f8-e4115b280940": "16",
    "20b2e0e5-9fe1-11e5-a9f8-e4115b280940": "17",
    "20b2e0e3-9fe1-11e5-a9f8-e4115b280940": "18",
    "20b2e0e4-9fe1-11e5-a9f8-e4115b280940": "19",
    "20b2e0dc-9fe1-11e5-a9f8-e4115b280940": "20",
    "20b2e0dd-9fe1-11e5-a9f8-e4115b280940": "21",
    "fb56990c-6a70-5b4d-8abc-ab04c0592585": "22",
    "589c9691-13d7-374b-860e-d154735e4144": "23",
    "b88a83cf-ccaa-ce40-bcf2-2071cad45238": "24",
    "a0905c3b-dc5e-11e5-8127-d6d6eb145c82": "25",
    "a0905c1c-dc5e-11e5-8127-d6d6eb145c82": "26",
    "aa29a512-6292-5246-9212-ddc82c87e69d": "27",
    "74e6d871-3c3c-e44e-ab1d-425a40e2222c": "28",
    "adcad8a3-e67e-11e8-b878-0050568204d6": "29",
    "37446653-ef03-11e8-a4aa-005056821322": "30",
    "a2866a80-1ea4-11eb-a826-0050568351d2": "31",
    "37446652-ef03-11e8-a4aa-005056821322": "32",
    "17797760-d8c7-11eb-ae63-0050568351d2": "33",
    "adcad8a2-e67e-11e8-b878-0050568204d6": "34",
    "7c737272-fed5-11e8-b79b-0050568204d6": "35",
    "93149ce1-2a63-11e7-98c6-005056821322": "36",
    "93149ce4-2a63-11e7-98c6-005056821322": "37",
    "93149ce2-2a63-11e7-98c6-005056821322": "38",
    "93149ce3-2a63-11e7-98c6-005056821322": "39",
    "d329ded3-253e-f84d-be15-b50c5dded15b": "40",
    "72103a9b-3bd0-e847-b45a-a3394690c142": "41",
    "bc8bfba3-c0dd-2a47-96c4-b6b13b7c8b1f": "42",
    "a46342bf-3271-a249-9a1b-fdbef1ab9399": "43",
    "20b2e0c9-9fe1-11e5-a9f8-e4115b280940": "44",
    "a780f43e-3a44-4c40-a3a3-8313eae7c5a3": "45",
    "7e66647b-b08b-b64d-a673-132bd9baf9df": "46",
    "a0425272-e423-a842-ac36-3341e5987642": "47",
    "dc480cee-1fc2-1f42-9aa7-8715c1dee43f": "48",
    "20b2e0ea-9fe1-11e5-a9f8-e4115b280940": "49",
    "0555a87f-5759-6c41-8147-f71cc462dd31": "50",
    "e6d95766-794d-8843-958b-c9ad79f059f9": "51",
    "1a87b5d3-e9bb-a145-af58-15a344dd3c37": "52",
    "d0d9192c-3586-464c-8593-5ab8d81f0065": "53",
    "8fbfb6c1-fea0-0849-a6bb-6b8bd938d1c7": "54",
    "bd0913d2-6236-224d-ab1b-efd9cb6f07ff": "55",
    "5138d9d1-be20-11e6-8004-005056825ca0": "56",
    "029e3ef2-3a1c-11e7-9c64-0050568204d6": "57",
    "5af09015-46e9-674c-a945-8965e6ee8924": "58",
    "544d88ce-38a1-9c42-8767-38830b7dbd33": "59",
    "eb89859b-7572-2d47-a029-3c0fcd6b0d5c": "60",
    "a0d63e62-99de-5240-9064-13f9148cc063": "61",
    "20b2e0cc-9fe1-11e5-a9f8-e4115b280940": "62",
    "20b2e0cd-9fe1-11e5-a9f8-e4115b280940": "63",
    "20b2e0cb-9fe1-11e5-a9f8-e4115b280940": "64",
    "de5b4e9a-7414-2945-a07b-be868f622b12": "65",
    "04111471-f4f2-11e6-9ae5-005056821322": "66",
    "e05ce512-8f88-11ea-a408-005056828ed3": "67",
    "20b2e0c7-9fe1-11e5-a9f8-e4115b280940": "68",
    "20b2e0eb-9fe1-11e5-a9f8-e4115b280940": "69",
    "383369b1-d404-11e6-bdf7-005056821322": "70",
    "M20b2e0d7-9fe1-11e5-a9f8-e4115b280940": "71",
    "70838ca1-e109-5749-bffd-10f797c00682": "72",
    "de5d401d-3575-d644-b742-6c16924a2f3f": "73",
    "b7c2021f-6966-9549-9ce6-3d15fd1d0320": "74",
    "9210e5d7-1777-1e47-a3eb-4b111c64e552": "75",
    "ca7a6ca0-3f58-204d-9bcc-6f8283e39a4b": "76",
    "e23b05fc-b219-6a4e-b527-bff8a0199be4": "77",
    "f4997408-710d-224d-9ba0-1bf7f9d9dd80": "78",
    "f96c9a70-64ea-9145-9009-d238c701653d": "79",
    "0acea628-5a90-3f4c-873f-d3d6e958cbed": "80",
    "1214f9fa-6374-4442-b4ba-cd2207549cf6": "81",
    "96af2847-09ad-984d-8860-5ceb12639323": "82",
    "751a9198-8cb8-7340-a78c-4ae5767ad9c3": "83",
    "20b2e0da-9fe1-11e5-a9f8-e4115b280940": "84",
    "fb487561-83fe-2b4a-b112-30b2d5252bab": "85",
    "76c1e0b9-4ce9-f84d-a86f-f5a47745634f": "86",
    "7cfa8233-2537-2f45-8a95-761e6eb9e25c": "87",
    "ddf060fe-8935-3f4c-845a-58e055d2b246": "88",
    "aede70a1-7b6b-11e7-b18a-0050568204d6": "89",
    "f6df39b1-d5ed-11e8-8474-005056821322": "90",
    "f6df39b3-d5ed-11e8-8474-005056821322": "91",
    "cda7bff1-e34d-11e8-8642-005056821322": "92",
    "ec24be92-fd67-11e8-9d80-0050568204d6": "93",
    "0ac98c02-9c69-11e8-aaaf-005056821322": "94",
    "01e95491-3c92-11e7-be59-0050568204d6": "95",
    "3eab876f-9343-2046-95e2-5de2bd8a355c": "96",
    "998aaf52-fd98-8e40-871c-df326ecb7ee4": "97",
    "12de8369-ae62-f341-89a0-29204dcf7f64": "98",
    "8e84f91c-dc92-7f40-a693-91d80ab33e6d": "99",
    "d1b0ab90-fe08-11e8-95c0-0050568204d6": "100",
    "20b2e0d5-9fe1-11e5-a9f8-e4115b280940": "101",
    "b1ea2321-299f-11e7-ad74-005056821322": "102",
    "20b2e0d4-9fe1-11e5-a9f8-e4115b280940": "103",
    "0ac98c04-9c69-11e8-aaaf-005056821322": "104",
    "d67e0624-6dcf-11e6-be2b-ba992a0501a6": "105",
    "d67e0623-6dcf-11e6-be2b-ba992a0501a6": "106",
    "ce8e9aa2-70e6-11e6-acbe-e635f0461918": "107",
    "410ab733-9202-11e6-8b61-82ab1fa1f30b": "108",
    "5cd23f51-dc82-11e5-9b2b-d6d6eb145c82": "109",
    "75df1ad1-ecf0-11e5-8623-aecc2fc6c3d7": "110",
    "54f7f1a1-af50-11e8-89d2-005056821322": "111",
    "54b55b1f-8662-3c4a-ba9b-290b104e7307": "112",
    "99411122-3b5f-ce42-8a2d-783d3c221e35": "113",
    "60958a81-3941-11e7-b258-0050568204d6": "114"
}


outputfileName = args.outputdirectory + "transformed_concepts.json"
publish_ids = args.outputdirectory + "publish_ids.json"

with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(concepts_file), outfile, ensure_ascii=False, indent=4)
