import json
import argparse
import os


parser = argparse.ArgumentParser()
parser.add_argument('-o', '--outputdirectory', help="the path to the directory of the output files", required=True)
args = parser.parse_args()


def transform(ds_file, mt_file):
    datasets = openfile(ds_file)
    media_types = openfile(mt_file)
    transformed_datasets = {}
    print("Total number of extracted datasets: " + str(len(datasets)))
    transformed_count = 0
    failed = {}
    for dataset_key in datasets:
        result = transform_dataset(datasets[dataset_key], media_types)
        if result["transformed"]:
            transformed_datasets[dataset_key] = result["transformed"]
            transformed_count += 1
        if len(result["failed"]) > 0:
            failed[dataset_key] = result["failed"]
    print("Total number of transformed datasets: " + str(transformed_count))
    with open("transform_errors.json", 'w', encoding="utf-8") as err_file:
        json.dump(failed, err_file, ensure_ascii=False, indent=4)
    return transformed_datasets


def transform_dataset(dataset, media_types):
    distribution = dataset.get("distribution")
    distribution = distribution if distribution else []
    modified_distributions = []
    failed_matches = []
    for dist in distribution:
        formats = dist.get("format")
        formats = formats if formats else []
        modified_formats = []

        for fmt in formats:
            modified_fmt = match_format(fmt, media_types)
            if modified_fmt:
                modified_formats.append(modified_fmt)
            else:
                failed_matches.append(fmt)
                if fmt:
                    modified_formats.append(fmt)
        modified_distribution = dist
        modified_distribution["format"] = modified_formats
        modified_distributions.append(modified_distribution)
    transformed_dataset = {}
    if len(modified_distributions) > 0:
        transformed_dataset["distribution"] = modified_distributions
        return {"transformed": transformed_dataset, "failed": failed_matches}
    else:
        return {"transformed": None, "failed": failed_matches}


def match_format(fmt, media_types):
    for media_type in media_types:
        if fmt == media_type.get("code"):
            return media_type.get("uri")
        elif fmt and "application/" + fmt == media_type.get("code"):
            return media_type.get("uri")
        elif fmt and fmt.lower() == media_type.get("name").lower():
            return media_type.get("uri")
        elif fmt == media_type.get("uri"):
            return fmt
    return None


def openfile(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)


datasets_file = args.outputdirectory + "mongo_datasets.json"
media_types_file = "media_types.json"
outputfileName = args.outputdirectory + "transformed_datasets.json"


with open(outputfileName, 'w', encoding="utf-8") as outfile:
    json.dump(transform(datasets_file, media_types_file), outfile, ensure_ascii=False, indent=4)
