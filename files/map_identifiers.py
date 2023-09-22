import json
import argparse
import requests

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()
outputfileName = args.outputdirectory + "mapped_identifiers.json"

brreg_published = requests.get("https://data.brreg.no/begrep/").json()
identifiers = {}
guids = {}
for item in brreg_published:
    print(item)
    if "http://data.brreg.no/begrep/" in item:
        identifiers[brreg_published[item]["http://www.w3.org/2008/05/skos-xl#prefLabel"][0]["value"]] = item
    elif "_:" in item and brreg_published[item].get("http://www.w3.org/2008/05/skos-xl#literalForm") is not None:
        guids[item] = brreg_published[item].get("http://www.w3.org/2008/05/skos-xl#literalForm")[0]["value"]

mapped = {}
for identifier in identifiers:
    if identifier in guids:
        mapped[guids[identifier]] = identifiers[identifier]

with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(mapped, outfile, ensure_ascii=False, indent=4)
