import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from utils import get_api_domain, get_headers
from urllib.parse import urljoin

concepts = ["/orgs/UVL-Burundi/sources/uvl-ciel/concepts/7898261/"]

all_mappings = []
ciel_concept = set()
name_mapping = {}


def fetch_all_mappings(concept):
    url = urljoin(urljoin(get_api_domain(), concept), "mappings/")
    params = {"limit": 100}
    mappings = []
    while url:
        response = requests.get(url, params=params, headers=get_headers())
        response.raise_for_status()
        data = response.json()
        mappings.extend(data)
        url = response.headers.get("next")
        params = {}
    print(concept, len(mappings))
    return mappings


with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(fetch_all_mappings, concept) for concept in concepts]
    for future in as_completed(futures):
        mappings = future.result()
        for mapping in mappings:
            if (
                mapping["map_type"]
                in {"CONCEPT-SET", "Q-AND-A"}
                # and mapping["to_source_owner"] == "CIEL"
            ):
                all_mappings.append(mapping)
                ciel_concept.add(mapping["to_concept_url"])
                # name_mapping[mapping["to_concept_name_resolved"]] = mapping[
                #     "to_concept_url"
                # ]


with open("./all_mappings.json", "w") as f:
    data = {
        "all_mappings": all_mappings,
        "ciel_concept": list(ciel_concept),
        "name_mapping": name_mapping,
        "mapping_urls": [mapping["url"] for mapping in all_mappings],
    }
    json.dump(data, f, indent=4)
