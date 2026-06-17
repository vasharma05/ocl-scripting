# Defining imports
import requests
import json
import os
from dotenv import load_dotenv, find_dotenv
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import time
from urllib.parse import urljoin, urlparse

# Defining constants
load_dotenv(find_dotenv())
OCL_API_DOMAIN = os.getenv("OCL_API_DOMAIN")
OCL_API_TOKEN = os.getenv("OCL_API_TOKEN")
COLLECTION_OR_SOURCE_URLS = [
    # "/orgs/UVL-Burundi/collections/uvl-drug-entry/v1/",
    # "/orgs/UVL-Burundi/collections/uvl-dx/",
    # "/orgs/UVL-Burundi/collections/uvl-labtests/",
    # "/orgs/UVL-Burundi/collections/uvl-procedures/",
    # "/orgs/UVL-Burundi/collections/uvl-forms/",
    # "/orgs/UVL-Burundi/collections/uvl-allergens/",
    # "/orgs/UVL-Burundi/collections/uvl-drugs/",
    # "/orgs/UVL-Burundi/sources/uvl-ciel/",
    # "/orgs/UVL-Burundi/sources/uvl-custom/",
    # "/orgs/MSFOCG/collections/TEMP-PIUS/",
    # "/orgs/MSFOCG/collections/iraq-mosul/"
    "/orgs/MSFOCG/collections/lime-emr/"
    # "/orgs/UVL-Burundi/collections/uvl-allergens/",
    # "/orgs/UVL-Burundi/collections/uvl-vital-signs/",
    # "/orgs/UVL-Burundi/collections/uvl-cause-of-death/",
    # "/orgs/UVL-Burundi/collections/uvl-immunizations/",
    # "/orgs/UVL-Burundi/collections/uvl-registration/",
]
COLLECTION_OR_SOURCE_NAME = "uvl-drug-entry"


# VARIABLES TO BE ADJUSTED BY USER
BASE_URL = f"{OCL_API_DOMAIN}"

headers = {
    "Authorization": f"Token {OCL_API_TOKEN}",
    "Content-Type": "application/json",
}


def fetch_references_page(
    url: str, headers: Dict[str, str], params: Dict[str, Any]
) -> requests.Response:
    """
    Fetch a single page of references from OCL.

    Args:
        url: The URL to fetch references from
        headers: Headers for the API request

    Returns:
        Response object containing the API response
    """
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response


def fetch_all_references(collection_or_source_url: str) -> List[Dict[str, Any]]:
    """
    Fetch all references from OCL with pagination support.

    Returns:
        List of all references
    """
    all_references = []
    next_url = urljoin(urljoin(BASE_URL, collection_or_source_url), "references/")
    print(next_url)
    params = {
        "limit": 100,
    }

    while next_url:
        print(f"Fetching references from: {next_url}")
        response = fetch_references_page(next_url, headers, params)

        # Add references from current page
        references_data = response.json()
        all_references.extend(references_data)

        # Get next page URL from headers
        next_url = response.headers.get("next")
        params = {}

        # Add a small delay to avoid rate limiting
        time.sleep(0.5)

    return all_references


def save_references_to_json(
    references: List[Dict[str, Any]], collection_or_source_name: str
):
    """
    Save concepts to a JSON file.

    Args:
        concepts: List of concepts to save
        output_file: Name of the output JSON file
    """
    output_file = f"all_{collection_or_source_name}_references.json"
    with open(output_file, "w") as f:
        data = {
            "all_references": references,
            "references_urls": [reference["uri"] for reference in references],
        }
        json.dump(data, f, indent=2)
    print(f"Saved {len(references)} references to {output_file}")


def main():
    for collection_or_source_url in COLLECTION_OR_SOURCE_URLS:
        # Fetch all concepts
        references = fetch_all_references(collection_or_source_url)

        # Save to JSON file
        save_references_to_json(references, collection_or_source_url.split("/")[-2])

    print(f"Total references fetched: {len(references)}")


if __name__ == "__main__":
    main()
