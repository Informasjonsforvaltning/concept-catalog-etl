import json
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()


#  TODO:
# Finn _id = concept-catalog (..) mongo_id , og _id = identifikator fra mapping og extract
# Kopier fdkId og issued fra data.brreg til concept-catalog, og slett data.brreg element etter load
