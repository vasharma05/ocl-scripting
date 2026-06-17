import os
from dotenv import load_dotenv, find_dotenv
from uuid import uuid4

# Load environment variables
load_dotenv(find_dotenv())

# Defining constants
OCL_API_DOMAIN = os.getenv("OCL_API_DOMAIN")
OCL_API_TOKEN = os.getenv("OCL_API_TOKEN")
print(OCL_API_TOKEN)
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
