# Defining imports
import requests
import json
import os
from dotenv import load_dotenv, find_dotenv
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from drug_resources import dosage_forms, drug_concepts
from common import (
    verify_concepts,
    check_in_collection,
    get_source_or_collection_url,
    check_in_collection_wrapper,
)


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


def process_drug_concept_response(concept_info, response, drug_concept_map):
    data = response.json()
    if len(data) == 0:
        print(f"No concept found for {concept_info}")
        return False
    elif len(data) > 1:
        print(f"Multiple concepts found for {concept_info}")
        return False

    result = data[0]
    concept_external_id, concept_name = concept_info
    drug_concept_map[concept_external_id] = {
        "name_in_sheet": concept_name,
        "name": result.get("display_name"),
        "concept_class": result.get("concept_class"),
        "id": result.get("id"),
        "url": result.get("url"),
        "external_id": concept_external_id,
    }

    if result.get("concept_class") != "Drug":
        print(
            f"Concept {concept_info} is not a drug, expected Drug but got {result.get('concept_class')}"
        )
        return False

    return True


def post_processing_drug_concepts(concepts, drug_concept_map):

    print("<<<<<<<<<<<<<<<<<<<<< CHECKING IN COLLECTION >>>>>>>>>>>>>>>>>>>>>>>>")

    collection_url = get_source_or_collection_url()
    check_in_collection_wrapper(collection_url, drug_concept_map, concepts)
    print("id|concept_external_id|name|name_in_sheet|concept_class|url|in_collection")

    for concept_external_id, concept_name in concepts:
        data = drug_concept_map.get(concept_external_id, {})
        id = data.get("id")
        print(
            f"{id}|{concept_external_id}|{data.get("name")}|{data.get("name_in_sheet")}|{data.get("concept_class")}|{data.get("url")}|{drug_concept_map[concept_external_id].get('in_collection')}"
        )


verify_concepts(
    get_source_or_collection_url(),
    drug_concepts,
    process_drug_concept_response,
    post_processing_drug_concepts,
)
