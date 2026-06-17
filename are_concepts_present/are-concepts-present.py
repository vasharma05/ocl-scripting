# Defining imports
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin
from are_concepts_present_resources import all_concepts
from common import get_api_domain, get_source_or_collection_url, get_headers
import time


concept_presence_map = {"present": {}, "absent": {}}

BATCH_SIZE = 300
DELAY_BETWEEN_BATCHES = 60


def verify_concepts_present(
    source_or_collection_url: str,
    concept_to_check: str,
    is_concept_url: bool,
) -> requests.Response:
    if is_concept_url:
        url = urljoin(
            urljoin(get_api_domain(), source_or_collection_url), "references/"
        )
        params = {"q": concept_to_check, "includeSearchMeta": True}
    else:
        url = urljoin(urljoin(get_api_domain(), source_or_collection_url), "concepts/")
        params = {"q": concept_to_check}
    try:
        response = requests.get(url, params=params, headers=get_headers())
        response.raise_for_status()
        return (concept_to_check, response)
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        return (concept_to_check, None)


def verify_concept_id(concept_to_check, response, is_concept_url):
    data = response.json()
    if response.status_code == 200:
        if len(data) != 1:
            if len(data) == 0:
                print(f"Concept {concept_to_check} is not present")
            else:
                print(f"Concept {concept_to_check} is present but has multiple results")
            concept_presence_map["absent"][concept_to_check] = None
            return False
        elif len(data) == 1:
            if not is_concept_url:
                print(
                    f"Concept {concept_to_check} with url: {data[0].get('url', '')} is present"
                )
                res = data[0]
                concept_presence_map["present"][concept_to_check] = res.get("url", "")
            else:
                print(
                    f"Concept {concept_to_check} with reference latest_source_version: {data[0].get('latest_source_version', '')} is present"
                )
                res = data[0]
                concept_presence_map["present"][concept_to_check] = res.get(
                    "latest_source_version", ""
                )
            return True
    else:
        print(f"Concept {concept_to_check} is not present: {response.status_code}")
        concept_presence_map["absent"][concept_to_check] = None
        return False


def verify_concept_url(concept_to_check, response):
    data = response.json()
    if response is None:
        print(f"Concept {concept_to_check} is not present: {response.status_code}")
    elif response.status_code == 200:
        print(f"Concept {concept_to_check} with url: {data.get('url')} is present")


def main(source_or_collection_url, concepts_to_check, is_concept_url):
    for i in range(0, len(concepts_to_check), BATCH_SIZE):
        batch = concepts_to_check[i : i + BATCH_SIZE]
        print(f"Processing batch {i} to {i + BATCH_SIZE - 1}")

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [
                executor.submit(
                    verify_concepts_present,
                    source_or_collection_url,
                    concept_to_check,
                    is_concept_url,
                )
                for concept_to_check in batch
            ]

        for future in as_completed(futures):
            concept_to_check, response = future.result()
            verify_concept_id(concept_to_check, response, is_concept_url)

        if i + BATCH_SIZE < len(concepts_to_check):
            time.sleep(DELAY_BETWEEN_BATCHES)


if __name__ == "__main__":
    is_concept_url = input("Is this a concept url? (y/n): ").strip() == "y"
    print(f"Checking {len(set(all_concepts))} concepts")
    main(get_source_or_collection_url(), list(set(all_concepts)), is_concept_url)
    with open("are_concepts_present/concept_present_map.json", "w") as f:
        file_data = {
            "present": concept_presence_map["present"],
            "absent": concept_presence_map["absent"],
            "present_concept_urls": list(concept_presence_map["present"].values()),
        }
        json.dump(file_data, f, indent=4)
