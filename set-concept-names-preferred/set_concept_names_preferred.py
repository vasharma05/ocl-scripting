"""
Set locale_preferred=true on an existing concept name in OCL.

For each concept_url in `resources.concept_names`:
- fetch the concept names (`GET {domain}/{concept_url}/names/`)
- when a name matches (same locale + name_type + exact name), mark it preferred
- all other names for that (locale + name_type) are marked non-preferred

If no name matches for a concept, it is recorded in the results file.
"""

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

from common import get_headers, get_api_domain
from resources import concept_names, locale_name, name_type, locale_preferred


def _normalize_concept_url(concept_url: str) -> str:
    concept_url = (concept_url or "").strip()
    if not concept_url.startswith("/"):
        concept_url = "/" + concept_url
    if not concept_url.endswith("/"):
        concept_url = concept_url + "/"
    return concept_url


def _names_url(concept_url: str) -> str:
    # Keep URL composition explicit to match `domain/concept_url/names`.
    base = get_api_domain().rstrip("/")
    concept_url = _normalize_concept_url(concept_url)
    return f"{base}{concept_url}names/"


def _fetch_names(concept_url: str) -> list:
    url = _names_url(concept_url)
    response = requests.get(url, headers=get_headers())
    response.raise_for_status()
    return response.json()


def _update_preferred_flag(names: list, expected_name: str):
    """
    Returns: (updated_names, match_found)
    """
    updated = []
    match_found = False
    preferred_set_for_expected = False

    for n in names:
        if not isinstance(n, dict):
            updated.append(n)
            continue

        n_locale = n.get("locale")
        n_type = n.get("name_type")
        n_name = n.get("name")

        if n_locale != locale_name:
            updated.append(n)
            continue

        # Target the specific name_type if the payload includes it; if it's missing,
        # still update this entry so the preferred name becomes deterministic.
        type_matches = n_type is None or n_type == name_type
        if not type_matches:
            updated.append(n)
            continue

        # Override name + name_type to the expected values.
        # Then mark only one entry as preferred.
        match_found = True
        n = {**n, "name": expected_name, "name_type": name_type}
        if not preferred_set_for_expected:
            n["locale_preferred"] = bool(locale_preferred)
            preferred_set_for_expected = True
        else:
            n["locale_preferred"] = False

        updated.append(n)

    return updated, match_found


def set_preferred_for_concept(concept_url: str, expected_concept_name: str):
    concept_url = _normalize_concept_url(concept_url)

    names = _fetch_names(concept_url)
    if not isinstance(names, list):
        raise ValueError("Unexpected payload: names endpoint did not return a list")

    updated_names, match_found = _update_preferred_flag(names, expected_concept_name)
    if not match_found:
        available = [
            {
                "name": n.get("name"),
                "name_type": n.get("name_type"),
                "locale_preferred": n.get("locale_preferred"),
            }
            for n in names
            if isinstance(n, dict) and n.get("locale") == locale_name and n.get("name")
        ]
        return {
            "concept_url": concept_url,
            "expected_name": expected_concept_name,
            "matched": False,
            "updated": False,
            "available_names_in_locale": available,
        }

    # PATCH only the names field (preferred approach used elsewhere in this repo).
    url = f"{get_api_domain().rstrip('/')}{concept_url}"
    response = requests.patch(url, headers=get_headers(), json={"names": updated_names})

    return {
        "concept_url": concept_url,
        "expected_name": expected_concept_name,
        "matched": True,
        "updated": response.status_code in (200, 201, 202, 204),
        "status_code": response.status_code,
        "body": response.text,
    }


if __name__ == "__main__":
    concept_items = list(concept_names.items())
    batch_size = 300

    preferred_set = {}
    no_match = {}
    failed = {}

    for i in range(0, len(concept_items), batch_size):
        batch = concept_items[i : i + batch_size]
        print(f"Processing batch {i} to {i + len(batch) - 1}")

        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_concept = {
                executor.submit(
                    set_preferred_for_concept, concept_url, concept_name
                ): concept_url
                for concept_url, concept_name in batch
            }

            for future in as_completed(future_to_concept):
                try:
                    result = future.result()
                    concept_url = result["concept_url"]

                    if not result["matched"]:
                        no_match[concept_url] = {
                            "expected_name": result["expected_name"],
                            "available_names_in_locale": result.get(
                                "available_names_in_locale", []
                            ),
                        }
                        print(f"NO MATCH for {concept_url}")
                    else:
                        if result.get("updated"):
                            preferred_set[concept_url] = result["expected_name"]
                            print(f"Preferred set for {concept_url}")
                        else:
                            failed[concept_url] = {
                                "expected_name": result["expected_name"],
                                "status_code": result.get("status_code"),
                                "body": result.get("body"),
                            }
                            print(f"FAILED update for {concept_url}")
                except Exception as e:
                    concept_url = future_to_concept[future]
                    failed[concept_url] = str(e)
                    print(f"ERROR in batch {i}: {e}")

        if i + batch_size < len(concept_items):
            time.sleep(30)

    output = {
        "locale_name": locale_name,
        "name_type": name_type,
        "locale_preferred": locale_preferred,
        "preferred_set": preferred_set,
        "no_match": no_match,
        "failed": failed,
    }

    output_path = Path(__file__).resolve().parent / "results.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(
        "Done. "
        f"Preferred set: {len(preferred_set)}, "
        f"No match: {len(no_match)}, "
        f"Failed: {len(failed)}. "
        "Output: set-concept-names-preferred/results.json"
    )
