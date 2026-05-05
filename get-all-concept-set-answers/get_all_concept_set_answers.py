"""
Fetch concept-set members and answer mappings for given concept set URL(s).

Behavior:
1) Read concept set URL(s) from resources.py (`concept_url`).
2) Fetch all mappings for each concept set (with pagination).
3) Collect member concepts from mappings where map_type is either "CONCEPT-SET" or "Q-AND-A".
4) For each member concept, fetch all mappings (with pagination), using multithreading.
5) Process member concepts in batches of 300.
6) Write results to get-all-concept-set-answers/results.json.
"""

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin

import requests

from common import get_api_domain, get_headers
from resources import concept_url


def normalize_concept_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    if not url.startswith("/"):
        url = "/" + url
    if not url.endswith("/"):
        url = f"{url}/"
    return url


def get_input_concept_urls():
    if isinstance(concept_url, str):
        normalized = normalize_concept_url(concept_url)
        return [normalized] if normalized else []

    if isinstance(concept_url, list):
        urls = []
        for item in concept_url:
            normalized = normalize_concept_url(item)
            if normalized:
                urls.append(normalized)
        return urls

    raise ValueError("`concept_url` in resources.py must be a string or a list of strings")


def fetch_all_mappings_for_concept(target_concept_url: str):
    next_url = urljoin(urljoin(get_api_domain(), target_concept_url), "mappings/")
    params = {"limit": 100}
    all_mappings = []

    while next_url:
        response = requests.get(next_url, headers=get_headers(), params=params)
        response.raise_for_status()
        all_mappings.extend(response.json())
        next_url = response.headers.get("next")
        params = {}

    return all_mappings


def extract_target_urls(mappings, map_types):
    if isinstance(map_types, str):
        map_types = {map_types}
    else:
        map_types = set(map_types)

    target_urls = []
    for mapping in mappings:
        if mapping.get("map_type") not in map_types:
            continue
        to_url = mapping.get("to_concept_url")
        if to_url:
            target_urls.append(to_url)
    return list(dict.fromkeys(target_urls))


def process_member_concept(member_concept_url: str):
    mappings = fetch_all_mappings_for_concept(member_concept_url)
    return {
        "concept_set": extract_target_urls(mappings, "CONCEPT-SET"),
        "answers": extract_target_urls(mappings, "Q-AND-A"),
        "all_mappings_count": len(mappings),
    }


if __name__ == "__main__":
    concept_set_urls = get_input_concept_urls()
    if not concept_set_urls:
        raise ValueError("No concept set URLs found in resources.py (`concept_url`).")

    all_concepts = []
    seen = set()

    def add_urls(urls):
        for url in urls:
            normalized = normalize_concept_url(url)
            if normalized and normalized not in seen:
                seen.add(normalized)
                all_concepts.append(normalized)

    for concept_set_url in concept_set_urls:
        print(f"Processing concept set: {concept_set_url}")
        add_urls([concept_set_url])

        try:
            concept_set_mappings = fetch_all_mappings_for_concept(concept_set_url)
            member_concepts = extract_target_urls(
                concept_set_mappings, ["CONCEPT-SET", "Q-AND-A"]
            )
            add_urls(member_concepts)
            print(f"Found {len(member_concepts)} member concept(s)")
        except Exception as e:
            print(f"Failed to fetch concept set mappings for {concept_set_url}: {e}")
            continue

        batch_size = 300
        for i in range(0, len(member_concepts), batch_size):
            batch = member_concepts[i : i + batch_size]
            print(f"Processing member batch {i} to {i + len(batch) - 1}")

            with ThreadPoolExecutor(max_workers=20) as executor:
                future_to_concept = {
                    executor.submit(process_member_concept, member_concept): member_concept
                    for member_concept in batch
                }

                for future in as_completed(future_to_concept):
                    member_concept = future_to_concept[future]
                    try:
                        concept_data = future.result()
                        add_urls(concept_data.get("concept_set", []))
                        add_urls(concept_data.get("answers", []))
                    except Exception as e:
                        print(f"Failed for {member_concept}: {e}")

    with open("get-all-concept-set-answers/results.json", "w") as f:
        json.dump(all_concepts, f, indent=2, ensure_ascii=False)

    print("Done. Output written to get-all-concept-set-answers/results.json")