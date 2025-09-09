import json
import os
import requests
from resources import (
    concepts_to_check,
    ENDPOINT_DOMAIN,
    OPENMRS_USERNAME,
    OPENMRS_PASSWORD,
    SEARCH_PARAMS,
)
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin
from requests.auth import HTTPDigestAuth
import base64

RESULTS_FILE = "verify-concepts-in-openmrs/concepts_verification_results.json"
REST_API_ENDPOINT = "/openmrs/ws/rest/v1/concept/"
ENDPOINT_TEMPLATE = urljoin(ENDPOINT_DOMAIN, REST_API_ENDPOINT)
MAX_WORKERS = 10  # You can adjust this based on your system/network


def check_concept_exists(uuid):
    url = urljoin(ENDPOINT_TEMPLATE, uuid)
    params = SEARCH_PARAMS
    try:
        response = requests.get(
            url,
            headers={
                "Authorization": f"Basic {base64.b64encode(f'{OPENMRS_USERNAME}:{OPENMRS_PASSWORD}'.encode()).decode()}"
            },
            params=params,
        )
        if response.status_code == 200:
            data = response.json()
            return uuid, data
        else:
            return uuid, None
    except Exception:
        return uuid, "Error"


def main():
    present = {}
    absent = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_uuid = {
            executor.submit(check_concept_exists, uuid): uuid
            for uuid in set(concepts_to_check)
        }
        for future in as_completed(future_to_uuid):
            uuid, data = future.result()
            if data:
                present[uuid] = data
            else:
                absent[uuid] = None
    with open(RESULTS_FILE, "w") as f:
        json.dump({"present": present, "absent": absent}, f)
    print(f"Results written to {RESULTS_FILE}")


if __name__ == "__main__":
    main()
