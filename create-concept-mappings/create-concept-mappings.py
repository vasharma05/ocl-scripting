# Defining imports
import sys
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
from common import (
    get_new_external_id,
    get_source_url,
    get_headers,
    get_api_domain,
)
from resources import mappings

# Defining constants
# VARIABLES TO BE ADJUSTED BY USER
BASE_URL = get_api_domain()

headers = get_headers()


def log_request_url(url: str, params: Dict = None):
    """Log the full URL being requested"""
    full_url = f"{url}"
    print(f"Requesting URL: {full_url} with data {params}")


def create_mapping(
    source_url: str, from_concept_url: str, to_concept_url: str, map_type: str
) -> bool:
    """Create a CONCEPT-SET mapping between two concepts"""
    mapping_url = urljoin(urljoin(BASE_URL, source_url), "mappings/")

    mapping_data = {
        "from_concept_url": from_concept_url,
        "to_concept_url": to_concept_url,
        "map_type": map_type,
        "external_id": get_new_external_id(),
    }

    print(f"Creating mapping from {from_concept_url} to {to_concept_url}")
    # log_request_url(mapping_url, mapping_data)
    response = requests.post(mapping_url, headers=headers, json=mapping_data)

    if response.status_code in [200, 201]:
        print(f"Successfully created mapping: {response.json().get('url')}")
        return True
    else:
        print(f"Failed to create mapping. Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return False


def main():
    """Main function to create all mappings"""
    success_count = 0
    failure_count = 0

    source_url = get_source_url()
    for from_concept, mapping_object in mappings.items():
        for map_type, to_concepts in mapping_object.items():
            for to_concept in to_concepts:
                if create_mapping(source_url, from_concept, to_concept, map_type):
                    print(
                        f"Successfully created {map_type} mapping from {from_concept} to {to_concept}"
                    )
                else:
                    print(
                        f"Failed to create {map_type} mapping from {from_concept} to {to_concept}"
                    )


if __name__ == "__main__":
    main()
