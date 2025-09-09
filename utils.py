import os
from dotenv import load_dotenv, find_dotenv
from uuid import uuid4
from urllib.parse import urljoin
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


# Load environment variables
load_dotenv(find_dotenv())

# Defining constants
OCL_API_DOMAIN = os.getenv("OCL_API_DOMAIN")
OCL_API_TOKEN = os.getenv("OCL_API_TOKEN")
BASE_URL = f"{OCL_API_DOMAIN}"
headers = {
    "Authorization": f"Token {OCL_API_TOKEN}",
    "Content-Type": "application/json",
}


def get_api_domain():
    return BASE_URL


def get_headers():
    return headers


def get_source_or_collection_url():
    org_name = input("Enter the org name: ")
    is_source = input("Is it a source? (y/n): ")
    source_or_collection_name = input("Enter the source or collection name: ")
    if is_source.lower() == "y":
        url = f"/orgs/{org_name}/sources/{source_or_collection_name}/"
    elif is_source.lower() == "n":
        url = f"/orgs/{org_name}/collections/{source_or_collection_name}/"
    else:
        raise ValueError("Invalid source or collection name")

    print("URL: ", url)
    return url


def get_file_name(collection_or_source_name):
    return f"all_{collection_or_source_name}_concepts.json"


def get_new_external_id():
    """Generate a new UUID for external ID"""
    return str(uuid4())


fetched_cache = set()


def fetch_all_mappings_for_concept(concept, reset_cache=False):
    print(fetched_cache)
    if concept in fetched_cache:
        return []
    fetched_cache.add(concept)
    # print(fetched_cache)
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
    return mappings


def get_all_related_concepts(concepts):
    all_concepts = set()
    all_concepts.update(concepts)
    print("starting")
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [
            executor.submit(fetch_all_mappings_for_concept, concept)
            for concept in concepts
        ]
        for future in as_completed(futures):
            mappings = future.result()
            # mapped_concepts = list(
            #     map(lambda mapping: mapping["to_concept_url"], mappings)
            # )
            mapped_concepts = list(
                map(lambda mapping: mapping["from_concept_url"], mappings)
            )
            all_concepts.update(get_all_related_concepts(mapped_concepts))
    fetched_cache.clear()
    return all_concepts
