import json
import requests
from utils import get_headers, get_api_domain
from urllib.parse import urljoin

# Load the updated mappings
with open("./mappings_updated.json", "r") as f:
    mappings = json.load(f)

# API configuration
api_domain = get_api_domain()
headers = get_headers()

# Create each mapping
for mapping in mappings:
    # Construct mapping URL
    source_url = "/orgs/UVL-Burundi/sources/uvl-ciel/"
    mappings_endpoint = urljoin(source_url, "mappings/")
    url = urljoin(api_domain, mappings_endpoint)

    # Make POST request to create mapping
    response = requests.post(url, json=mapping, headers=headers)

    if response.status_code == 201:
        print(
            f"Created mapping from {mapping['from_concept_url']} to {mapping['to_concept_url']}"
        )
    else:
        print(f"Failed to create mapping: {response.status_code}")
        print(response.text)
