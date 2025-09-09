# Defining imports
import requests
import json
import os
from dotenv import load_dotenv, find_dotenv
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from drug_resources import dosage_forms, drug_concepts
from common import (
    verify_concepts,
    get_dosing_unit_mappings,
    get_source_or_collection_url,
    check_in_collection_wrapper,
)

############### DRUG DOSAGE FORMS ###############


def is_concept_set(all_mappings, concept_id):
    return any(mapping.get("to_concept_code") == concept_id for mapping in all_mappings)


def process_dosage_form_response_wrapper(all_dosing_units_mappings):
    return lambda concept_info, response, concept_map: process_dosage_form_response(
        concept_info, response, concept_map, all_dosing_units_mappings
    )


def process_dosage_form_response(
    concept_info, response, concept_map, all_dosing_units_mappings
):
    concept_external_id, concept_name = concept_info
    data = response.json()
    if len(data) == 0:
        print(f"No dosage form found for {concept_external_id}")
        return False
    elif len(data) > 1:
        print(f"Multiple dosage forms found for {concept_external_id}")
        return False

    result = data[0]
    concept_map[concept_external_id] = {
        "name_in_sheet": concept_name,
        "name": result.get("display_name"),
        "concept_class": result.get("concept_class"),
        "id": result.get("id"),
        "url": result.get("url"),
        "external_id": concept_external_id,
    }

    if not is_concept_set(all_dosing_units_mappings, result.get("id")):
        print(
            f"Concept {concept_external_id} {concept_name} is not a concept set, expected {result.get('id')} to be set member of 'Dosing unit'"
        )
        return False

    return True


def post_processing_dosage_forms_wrapper(all_dosing_units_mappings):
    return lambda concepts, concept_map: post_processing_dosage_forms(
        concepts, concept_map, all_dosing_units_mappings
    )


def post_processing_dosage_forms(concepts, concept_map, all_dosing_units_mappings):
    print("<<<<<<<<<<<<<<<<<<<<< CHECKING IN COLLECTION >>>>>>>>>>>>>>>>>>>>>>>>")

    print(
        "id|concept_external_id|name|name_in_sheet|concept_class|url|is_set_member|in_collection"
    )

    collection_url = get_source_or_collection_url()
    check_in_collection_wrapper(collection_url, concept_map, concepts)

    for concept_external_id, concept_name in concepts:
        data = concept_map.get(concept_external_id, {})
        id = data.get("id")
        print(
            f"{id}|{concept_external_id}|{data.get("name")}|{data.get("name_in_sheet")}|{data.get("concept_class")}|{data.get("url")}|{is_concept_set(all_dosing_units_mappings, data.get("id"))}|{concept_map[concept_external_id].get('in_collection')}"
        )
    print("<<<<<<<<<<<<<<<<<<<<< CHECKING IN COLLECTION DONE >>>>>>>>>>>>>>>>>>>>>>>>")


all_dosing_units_mappings = get_dosing_unit_mappings(
    "/orgs/MSF/sources/MSF/concepts/3724/"
)


verify_concepts(
    get_source_or_collection_url(),
    dosage_forms,
    process_dosage_form_response_wrapper(all_dosing_units_mappings),
    post_processing_dosage_forms_wrapper(all_dosing_units_mappings),
)
