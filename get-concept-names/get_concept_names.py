"""
Fetch names for concepts in the requested locale using multithreading.
Inputs are loaded from `resources.py`:
  - concept_urls: list[str]
  - locale: str
"""

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin

import requests

from common import get_api_domain, get_headers
from resources import concept_urls, locale


def get_concept_names_for_locale(concept_url):
    url = urljoin(urljoin(get_api_domain(), concept_url), "names/")
    response = requests.get(url, headers=get_headers())
    response.raise_for_status()

    names_payload = response.json()

    preferred_name = None

    for n in names_payload:
        if (
            n.get("locale") == locale
            and n.get("locale_preferred") == True
            and n.get("name")
        ):
            preferred_name = n.get("name")
            break

    if preferred_name:
        return concept_url, preferred_name, True

    # Fallback: any name in the locale
    any_names = [n.get("name") for n in names_payload if n.get("locale") == locale]
    return concept_url, any_names, False


if __name__ == "__main__":
    preferred_results = {}
    non_preferred_results = {}
    errors = {}
    batch_size = 300

    for i in range(0, len(concept_urls), batch_size):
        batch = concept_urls[i : i + batch_size]
        print(f"Processing batch {i} to {i + len(batch) - 1}")

        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_url = {
                executor.submit(get_concept_names_for_locale, url): url for url in batch
            }

            for future in as_completed(future_to_url):
                concept_url = future_to_url[future]
                try:
                    concept_url, name, is_preferred = future.result()
                    if is_preferred:
                        preferred_results[concept_url] = name
                        print(f"Fetched preferred name for {concept_url}")
                    else:
                        non_preferred_results[concept_url] = name
                        print(f"No preferred/any name found for {concept_url}")
                except Exception as e:
                    errors[concept_url] = str(e)
                    print(f"Failed to fetch concept names for {concept_url}: {e}")

        if i + batch_size < len(concept_urls):
            time.sleep(30)

    output = {
        "locale": locale,
        "total_concepts": len(concept_urls),
        "preferred_results": preferred_results,
        "non_preferred_results": non_preferred_results,
        "errors": errors,
    }

    with open("get-concept-names/results.json", "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(
        f"Done. Preferred: {len(preferred_results)} concepts, "
        f"No-name: {len(non_preferred_results)} concepts, Failed: {len(errors)}. "
        "Output: get-concept-names/results.json"
    )
