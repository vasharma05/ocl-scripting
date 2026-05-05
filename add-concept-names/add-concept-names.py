"""
Running this file should pick the `concept_names` concept and then add french name to the concept in OCL. This should use multithreading to add the names to the concept in OCL.
"""

import time
from common import get_headers, get_api_domain
from add_concept_name_resources import (
    concept_names,
    locale_name,
    name_type,
    locale_preferred,
)
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin
import requests


def add_concept_name(concept_url, concept_name):
    url = urljoin(urljoin(get_api_domain(), concept_url), "names/")
    print(url, concept_name)
    headers = get_headers()
    response = requests.post(
        url,
        headers=headers,
        json={
            "name": concept_name,
            "locale": locale_name,
            "name_type": name_type,
            "locale_preferred": locale_preferred,
        },
    )
    return concept_name, response


if __name__ == "__main__":
    concept_items = list(concept_names.items())
    batch_size = 300

    for i in range(0, len(concept_items), batch_size):
        batch = concept_items[i : i + batch_size]
        print(f"Processing batch {i} to {i + len(batch) - 1}")

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [
                executor.submit(add_concept_name, concept_url, concept_name)
                for concept_url, concept_name in batch
            ]
            for future in as_completed(futures):
                concept_name, response = future.result()
                if response.status_code == 201:
                    print(f"Concept {concept_name} added successfully")
                else:
                    print(
                        f"Failed to add concept {concept_name}: {response.status_code} {response.text}"
                    )
        if i + batch_size < len(concept_items):
            time.sleep(30)
