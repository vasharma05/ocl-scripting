import requests
from common import get_headers, get_api_domain, get_collection_url
from remove_reference_resources import all_references
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
import json


def delete_reference(reference_url):
    url = urljoin(get_api_domain(), reference_url)
    try:
        response = requests.delete(url, headers=get_headers())
        print(url, response.text)
        response.raise_for_status()
    except Exception as e:
        print(f"{reference_url}: failed to delete due to {e}")
        return


if __name__ == "__main__":

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [
            executor.submit(delete_reference, reference_url)
            for reference_url in all_references
        ]
        for future in as_completed(futures):
            future.result()

    # for reference_url in all_references:
    #     delete_reference(reference_url)
