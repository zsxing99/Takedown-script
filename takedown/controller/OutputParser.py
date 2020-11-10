"""
OutputParser
--------------------------------------------------
output parser that converts the intermediate results to files or console
"""

import json
import yaml
import datetime


def date_time_converter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


def parse_intermediate_results(intermediate_results: dict, output_format: str, output_path: str):
    print("Start parsing output as {} format. to '{}'".format(output_format, output_path))
    final_results = []
    for user in intermediate_results:
        repos = intermediate_results[user].pop("repos")
        final_results.append({
            **intermediate_results[user],
            "repos": [repos[name] for name in repos]
        })

    # format output text
    text = None
    if output_format == "json":
        text = json.dumps({
            "results": final_results
        }, indent=2, default=date_time_converter)
    elif output_format == "yaml":
        text = yaml.dump({
            "results": final_results
        }, default_flow_style=False)

    # if no output file path provided
    if not output_path:
        print(text)
    else:
        with open(output_path, "w+") as file:
            file.write(text)

    return True


def parse_final_results(final_results: dict, output_format: str, output_path: str):
    # format output text
    text = None
    if output_format == "json":
        text = json.dumps(final_results, indent=2, default=date_time_converter)
    elif output_format == "yaml":
        text = yaml.dump(final_results, default_flow_style=False)

    # if no output file path provided
    if not output_path:
        print(text)
    else:
        with open(output_path, "w+") as file:
            file.write(text)

    return True

