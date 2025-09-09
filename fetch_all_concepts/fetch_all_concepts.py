# Defining imports
import requests
import json
import os
import pandas as pd
from dotenv import load_dotenv, find_dotenv
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import time
from urllib.parse import urljoin, urlparse


def get_file_name(collection_or_source_name):
    return f"fetch_all_concepts/all_{collection_or_source_name}_concepts.json"


# Defining constants
load_dotenv(find_dotenv())
OCL_API_DOMAIN = os.getenv("OCL_API_DOMAIN")
OCL_API_TOKEN = os.getenv("OCL_API_TOKEN")
COLLECTION_OR_SOURCE_URLS = [
    # "/orgs/UVL-Burundi/collections/uvl-drug-entry/",
    "/orgs/UVL-Burundi/collections/uvl-dx/",
    "/orgs/UVL-Burundi/collections/uvl-labtests/",
    "/orgs/UVL-Burundi/collections/uvl-procedures/",
    # "/orgs/UVL-Burundi/collections/uvl-forms/",
    # "/orgs/UVL-Burundi/collections/uvl-drugs/",
    # "/orgs/UVL-Burundi/sources/uvl-ciel/",
    # "/orgs/UVL-Burundi/sources/uvl-custom/",
    # "/orgs/MSFOCG/collections/TEMP-PIUS/",
    # "/orgs/MSFOCG/collections/iraq-mosul/"
]
COLLECTION_OR_SOURCE_NAME = "uvl-drug-entry"


# VARIABLES TO BE ADJUSTED BY USER
BASE_URL = f"{OCL_API_DOMAIN}"

headers = {
    "Authorization": f"Token {OCL_API_TOKEN}",
    "Content-Type": "application/json",
}


def fetch_concepts_page(
    url: str, headers: Dict[str, str], params: Dict[str, Any]
) -> requests.Response:
    """
    Fetch a single page of concepts from OCL.

    Args:
        url: The URL to fetch concepts from
        headers: Headers for the API request

    Returns:
        Response object containing the API response
    """
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response


def fetch_all_concepts(collection_or_source_url: str) -> List[Dict[str, Any]]:
    """
    Fetch all concepts from OCL with pagination support.

    Returns:
        List of all concepts
    """
    all_concepts = []
    next_url = urljoin(urljoin(BASE_URL, collection_or_source_url), "concepts/")
    print(next_url)
    params = {"limit": 100}

    while next_url:
        print(f"Fetching concepts from: {next_url}")
        response = fetch_concepts_page(next_url, headers, params)

        # Add concepts from current page
        concepts_data = response.json()
        all_concepts.extend(concepts_data)

        # Get next page URL from headers
        next_url = response.headers.get("next")
        params = {}

        # Add a small delay to avoid rate limiting
        time.sleep(0.5)

    return all_concepts


def save_concepts_to_json(
    concepts: List[Dict[str, Any]], collection_or_source_name: str
):
    """
    Save concepts to a JSON file.

    Args:
        concepts: List of concepts to save
        output_file: Name of the output JSON file
    """
    output_file = get_file_name(collection_or_source_name)
    with open(output_file, "w") as f:
        json.dump(concepts, f, indent=2)
    print(f"Saved {len(concepts)} concepts to {output_file}")


def main():
    for collection_or_source_url in COLLECTION_OR_SOURCE_URLS:
        # Fetch all concepts
        concepts = fetch_all_concepts(collection_or_source_url)

        # Save to JSON file
        save_concepts_to_json(concepts, collection_or_source_url.split("/")[-2])

    print(f"Total concepts fetched: {len(concepts)}")


if __name__ == "__main__":
    main()
