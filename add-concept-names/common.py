# Defining imports
import requests
import json
import os
from dotenv import load_dotenv, find_dotenv
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin

# Load environment variables
load_dotenv(find_dotenv())

# Defining constants
OCL_API_DOMAIN = os.getenv("OCL_API_DOMAIN")
OCL_API_TOKEN = os.getenv("OCL_API_TOKEN")


def get_headers():
    return {
        "Authorization": f"Token {OCL_API_TOKEN}",
        "Content-Type": "application/json",
    }


def get_api_domain():
    return OCL_API_DOMAIN


def get_collection_url():
    org_name = input("Enter the organization name: ")
    collection_name = input("Enter the collection name: ")
    return f"/orgs/{org_name}/collections/{collection_name}/"
