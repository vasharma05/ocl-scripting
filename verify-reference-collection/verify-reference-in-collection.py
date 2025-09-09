import requests
from common import get_headers, get_api_domain, get_collection_url
from resources import concepts
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin
import json


def verify_reference_in_collection(collection_url, concept_url):
    url = urljoin(urljoin(get_api_domain(), collection_url), "references")
    response = requests.get(
        url,
        headers=get_headers(),
        params={"q": concept_url},
    )
    print(url, concept_url)
    return concept_url, response


if __name__ == "__main__":
    results = {}
    collection_url = get_collection_url()
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [
            executor.submit(verify_reference_in_collection, collection_url, concept)
            for concept in concepts
        ]
        for future in as_completed(futures):
            concept_url, response = future.result()
            print(concept_url)
            if response.status_code == 200:
                data = response.json()
                if len(data) == 1 and data[0]["include"]:
                    results[concept_url] = {
                        "status": "success",
                        "message": "Reference found in collection",
                        "data": data,
                        "excludes": False,
                        "unresolved": any(
                            item["last_resolved_at"] is None for item in data
                        ),
                    }
                else:
                    results[concept_url] = {
                        "status": "error",
                        "message": "Reference not found in collection",
                        "data": data,
                        "excludes": any(not item["include"] for item in data),
                        "unresolved": any(
                            item["last_resolved_at"] is None for item in data
                        ),
                    }
            else:
                results[concept_url] = {
                    "status": "error",
                    "message": "Error verifying reference in collection",
                    "data": response.text,
                }
    with open("./verify-reference-collection/results.json", "w") as f:
        json.dump(results, f, indent=2)
