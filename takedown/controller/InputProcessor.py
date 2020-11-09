"""
InputReader
--------------------------------------------------
Input Reader that loads previous output files
"""

import yaml
import json


def load_previous_outputs_as_inputs(file_paths: list) -> dict:
    print("Start loading input files...")
    previous_records = {}
    for file_path in file_paths:
        print("Loading {}...".format(file_path))
        # start reading files
        data = None
        input_stream = open(file_path)
        # try yaml and json
        try:
            data = yaml.safe_load(input_stream)
            print("{} successfully loaded as yaml file.".format(file_path))
        except yaml.YAMLError:
            data = None
        if not data:
            try:
                data = json.load(input_stream)
                print("{} successfully loaded as json file.".format(file_path))
            except json.JSONDecodeError:
                data = None
        if not data or not isinstance(data, dict):
            print("Loading {} failed both in yaml and json. Skipped.".format(file_path))
            input_stream.close()
            continue
        input_stream.close()

        # read data into dict and merge data if necessary
        for user_dict in data["results"]:
            if user_dict["owner__username"] in previous_records:
                to_merge_user_object = previous_records[user_dict["owner__username"]]
                # iterate all repos in data
                for repo_object in user_dict["repos"]:
                    # update to the latest scanned ones
                    repo_name = repo_object["repo__name"]
                    if repo_name in to_merge_user_object["repos"]:
                        if repo_object["latest_detected_date"] > \
                                to_merge_user_object["repos"][repo_name]["latest_detected_date"]:
                            to_merge_user_object["repos"][repo_name]["latest_detected_date"] = \
                                repo_object["latest_detected_date"]
                            to_merge_user_object["repos"][repo_name]["status"] = repo_object["status"]
                    # or add the repos if no collision
                    else:
                        to_merge_user_object["repos"][repo_name] = {
                            **repo_object
                        }
            else:
                previous_records[user_dict["owner__username"]] = {
                    **user_dict,
                    "repos": {
                        repo_object["repo__name"]: {**repo_object} for repo_object in user_dict["repos"]
                    }
                }

    print("Inputs loading finished.")
    return previous_records

