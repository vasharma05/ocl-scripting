from drug_resources import dosage_forms, drug_concepts
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin
import requests
import os
from dotenv import load_dotenv, find_dotenv

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


def verify_concepts(source_or_collection_url, concepts, process_func, post_processing):
    print("STARTED")

    concept_map = {}
    success_count = 0
    failure_count = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(verify_concept, source_or_collection_url, concept)
            for concept in concepts
        ]

        for future in as_completed(futures):
            concept_info, response = future.result()
            if response is None:
                print(f"No response for {concept_info}")
                failure_count += 1
            elif process_func(concept_info, response, concept_map):
                success_count += 1
            else:
                failure_count += 1

        post_processing(concepts, concept_map)

    print(f"Success count: {success_count}")
    print(f"Failure count: {failure_count}")
    return (concept_map, success_count, failure_count)


def verify_concept(source_or_collection_url, concept_info):

    concept_external_id, concept_name = concept_info
    params = {"q": concept_external_id}
    try:
        response = requests.get(
            urljoin(urljoin(BASE_URL, source_or_collection_url), "concepts"),
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        return concept_info, response
    except Exception as e:
        print(f"Error verifying concept {concept_info}: {e}")
        return concept_info, None


def filter_mapping(mapping):
    return mapping.get("map_type") == "CONCEPT-SET"


def get_dosing_unit_mappings(concept_url):
    params = {"limit": 100}
    url = urljoin(urljoin(BASE_URL, concept_url), "mappings")
    all_mappings = []
    while url:
        response = requests.get(url, params=params, headers=headers)
        url = response.headers.get("next")
        params = {}
        response.raise_for_status()
        data = response.json()
        all_mappings.extend(data)
    return list(filter(filter_mapping, all_mappings))


def check_in_collection(source_or_collection_url, concept_map, concept_external_id):
    concept_id = concept_map.get(concept_external_id, {}).get("id")
    if not concept_id:
        return (False, concept_external_id)
    url = urljoin(urljoin(BASE_URL, source_or_collection_url), "concepts", concept_id)
    response = requests.get(url, headers=headers)
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return (True, concept_external_id)
    except Exception as e:
        print(f"Error checking in collection {concept_id}: {e}")
        return (False, concept_external_id)


def check_in_collection_wrapper(collection_url, concept_map, concepts):
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(
                check_in_collection,
                collection_url,
                concept_map,
                concept_external_id,
            )
            for concept_external_id, concept_name in concepts
        ]
        for future in as_completed(futures):
            is_present, concept_external_id = future.result()
            concept_map[concept_external_id]["in_collection"] = is_present


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
