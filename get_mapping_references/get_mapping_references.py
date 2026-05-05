import json
import requests
from urllib.parse import urljoin
from resources import concept_urls
from common import get_api_domain, get_headers, get_source_or_collection_url
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_mappings(concept_url):
    url = urljoin(urljoin(get_api_domain(), concept_url), "mappings/")
    params = {"limit": 100}
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
            lambda x: x["from_concept_url"] == concept_url
            or x["to_concept_url"] == concept_url,
            all_mappings,
        )
    )

    return (concept_url, all_mappings)


def start():
    all_mappings = {}
    concept_urls_set = set(concept_urls)
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(get_mappings, concept_url)
            for concept_url in concept_urls_set
        ]
        for future in as_completed(futures):
            id, mappings = future.result()
            all_mappings[id] = mappings
    with open("./get_mapping_references/results.json", "w") as f:
        json.dump(all_mappings, f)


if __name__ == "__main__":
    start()
