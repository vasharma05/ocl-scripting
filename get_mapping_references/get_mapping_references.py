import json
import requests
from urllib.parse import urljoin
from resources import concept_ids
from common import get_api_domain, get_headers, get_source_or_collection_url
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_mappings(collection_or_source_url, q):
    url = urljoin(urljoin(get_api_domain(), collection_or_source_url), "mappings/")
    params = {"limit": 100, "q": q}
    all_mappings = []
    while url:
        print(url)
        response = requests.get(url, params=params, headers=get_headers())
        response.raise_for_status()
        data = response.json()
        all_mappings.extend(data)
        params = {}
        url = response.headers.get("next")

    all_mappings = list(
        filter(
            lambda x: x["from_concept_code"] == q or x["to_concept_code"] == q,
            all_mappings,
        )
    )

    return (q, all_mappings)


def start():
    collection_or_source_url = get_source_or_collection_url()
    all_mappings = {}
    concept_ids_set = set(concept_ids)
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(get_mappings, collection_or_source_url, id)
            for id in concept_ids_set
        ]
        for future in as_completed(futures):
            id, mappings = future.result()
            all_mappings[id] = mappings
    with open("./get_mapping_references/results.json", "w") as f:
        json.dump(all_mappings, f)


if __name__ == "__main__":
    start()
