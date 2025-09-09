import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin
import requests
import os
from dotenv import load_dotenv, find_dotenv
from common import get_api_domain, get_headers, get_source_or_collection_url
from diagnoses_resources import all_diagnosis


def find_exact_match(results, diagnosis):
    for result in results:
        if result["external_id"] == diagnosis:
            return result
    return None


def verify_diagnosis(source_or_collection_url, diagnosis, concept_class):
    url = urljoin(
        urljoin(get_api_domain(), source_or_collection_url),
        "concepts",
    )
    print("URL: ", url)
    params = {"limit": 100, "q": diagnosis, "conceptClass": concept_class}

    first_search = True
    exact_match = None
    try:
        while url:
            print(url)
            response = requests.get(url, headers=get_headers(), params=params)
            response.raise_for_status()
            # url = response.headers.get("next")
            url = None
            params = {}
            data = response.json()
            exact_match = find_exact_match(data, diagnosis)
            if exact_match is not None:
                print(f"Exact match found for diagnosis: {diagnosis}")
                return diagnosis, exact_match, data
            print(f"Fuzzy {len(data)} match found for diagnosis: {diagnosis}")
            return diagnosis, None, data
        return diagnosis, exact_match, data
    except requests.exceptions.RequestException as e:
        print(f"Error verifying diagnosis {diagnosis}: {e}")
        return diagnosis, None, []


def verify_all_diagnosis(source_or_collection_url, all_diagnosis, concept_class):
    diagnosis_map = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(
                verify_diagnosis, source_or_collection_url, diagnosis, concept_class
            )
            for diagnosis in all_diagnosis
        ]

        for future in as_completed(futures):
            diagnosis, exact_match, results = future.result()
            diagnosis_map[diagnosis] = {
                "count": len(results) if exact_match is None else 1,
                "exact_match": exact_match,
                "results": results,
            }
        for diagnosis in all_diagnosis:
            data = diagnosis_map[diagnosis]
            print(
                f"{diagnosis}|{data['exact_match']['display_name'] if data['exact_match'] else 'None'}|{data['exact_match']['url'] if data['exact_match'] else 'None'}|{data.get('count', 0)}"
            )

    with open("msf-diagnoses/diagnosis_map.json", "w") as f:
        json.dump(diagnosis_map, f, indent=4)


if __name__ == "__main__":
    verify_all_diagnosis(get_source_or_collection_url(), all_diagnosis, "Diagnosis")
