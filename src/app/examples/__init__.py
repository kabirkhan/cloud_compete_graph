import json


def load_examples():
    with open("src/app/examples/batch_request.json") as br_file:
        batch_request = json.load(br_file)
    with open("src/app/examples/azure_cognitive_search_request.json") as azr_file:
        azure_cognitive_search_request = json.load(azr_file)

    return batch_request, azure_cognitive_search_request
