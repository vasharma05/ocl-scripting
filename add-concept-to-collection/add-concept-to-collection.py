from common import get_headers, get_api_domain, get_collection_url
from urllib.parse import urljoin
import requests
from add_concept_resources import concept_urls_to_add
import time
import math
import json

all_data = {}


def populateCollection(collection_url, concepts_to_add):
    url = urljoin(urljoin(get_api_domain(), collection_url), "references/")
    print(f"Adding concepts to {url}")

    params = {
        "cascade": '{"method":"sourcetoconcepts","cascade_levels":"*","map_types":"Q-AND-A,CONCEPT-SET","return_map_types":"*"}',
        "transformReferences": "extensional",
    }

    batch_size = 50
    results = []

    for i in range(0, len(concepts_to_add), batch_size):
        print(f"Processing batch {i} to {i + batch_size - 1}")
        batch = concepts_to_add[i : i + batch_size]
        try:
            response = requests.put(
                url,
                headers=get_headers(),
                json={
                    "data": [{"expression": concept_url} for concept_url in batch],
                    "cascade": {
                        "method": "sourcetoconcepts",
                        "cascade_levels": "*",
                        "map_types": "Q-AND-A,CONCEPT-SET",
                        "return_map_types": "*",
                    },
                },
                params=params,
            )
            print(response.text)
            if response.status_code not in [200, 201, 202]:
                errorBody = response.text
                raise Exception(
                    f"Failed to populate collection: {i} batch {response.status_code}\nResponse body: {errorBody}"
                )
        except Exception as e:
            all_data[i] = {
                "data": {},
                "error": str(e),
                "batch": batch,
            }
            continue
        print("Saved")
        data = response.json()
        all_data[i] = {
            "data": data,
            "error": None,
            "batch": batch,
        }
        results.append(data)
        time.sleep(5)
    return results


if __name__ == "__main__":
    collection_url = get_collection_url()
    populateCollection(collection_url, concept_urls_to_add)
    with open("add-concept-to-collection/all_data.json", "w") as f:
        json.dump(all_data, f)
