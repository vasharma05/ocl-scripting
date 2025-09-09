# Defining imports
import requests
import json
import os
from dotenv import load_dotenv, find_dotenv
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
from uuid import uuid4

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


def get_source_url():
    org_name = input("Enter the organization name: ")
    source_name = input("Enter the source name: ")
    print(f"Source URL: /orgs/{org_name}/sources/{source_name}/")
    return f"/orgs/{org_name}/sources/{source_name}/"


def get_new_external_id():
    return str(uuid4())
