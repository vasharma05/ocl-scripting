import requests
from common import get_api_domain, get_headers, get_source_url
from urllib.parse import urljoin


def build_concept_object(concept_class, datatype, names, descriptions=None):
    concept = {
        "concept_class": concept_class,
        "datatype": datatype,
        "names": names,
    }
    if descriptions:
        concept["descriptions"] = descriptions
    return concept


def send_to_ocl(collection_or_source_url, concept):
    url = urljoin(urljoin(get_api_domain(), collection_or_source_url), "concepts/")
    print(url)
    resp = requests.post(url, json=concept, headers=get_headers())
    if resp.status_code in (200, 201, 208):
        print(
            f"✅ Concept '{concept['names'][0]['name']}' processed: HTTP {resp.status_code}"
        )
    else:
        print(f"❌ Failed with HTTP {resp.status_code}")
        print(resp.text)


def create_name(name, locale, locale_preferred=True, name_type="Fully-Specified"):
    return {
        "name": name,
        "locale": locale,
        "locale_preferred": locale_preferred,
        "name_type": name_type,
    }


concepts = [
    {
        "concept_class": "Procedure",
        "datatype": "Text",
        "names": [
            create_name("EC01 - Abdominal ultrasound", "en"),
            create_name("EC01 - Échographie abdominale", "fr"),
        ],
    },
    {
        "concept_class": "Procedure",
        "datatype": "Text",
        "names": [
            create_name("EC02 - Gastrointestinal ultrasound", "en"),
            create_name("EC02 - Échographie gastro-intestinale", "fr"),
        ],
    },
    {
        "concept_class": "Procedure",
        "datatype": "Text",
        "names": [
            create_name("RX01 - Chest X-ray", "en"),
            create_name("RX01 - Radiographie thoracique", "fr"),
        ],
    },
    {
        "concept_class": "Procedure",
        "datatype": "Text",
        "names": [
            create_name("RX02 - Abdominal X-ray (plain)", "en"),
            create_name("RX02 - Radiographie abdominale (plaine)", "fr"),
        ],
    },
    {
        "concept_class": "Procedure",
        "datatype": "Text",
        "names": [
            create_name("RX03 - Bone X-ray", "en"),
            create_name("RX03 - Radiographie osseuse", "fr"),
        ],
    },
    {
        "concept_class": "Procedure",
        "datatype": "Text",
        "names": [
            create_name("RX04 - Intravenous urography", "en"),
            create_name("RX04 - Urographie intraveineuse", "fr"),
        ],
    },
    {
        "concept_class": "Procedure",
        "datatype": "Text",
        "names": [
            create_name("RX05 - Salpingo-urethrogram", "en"),
            create_name("RX05 - Salpingo-urethrographie", "fr"),
        ],
    },
    {
        "concept_class": "Procedure",
        "datatype": "Text",
        "names": [
            create_name("RX06 - Barium enema", "en"),
            create_name("RX06 - Enema au baryum", "fr"),
        ],
    },
    {
        "concept_class": "Procedure",
        "datatype": "Text",
        "names": [
            create_name("RX07 - CT scan", "en"),
            create_name("RX07 - Scanner CT", "fr"),
        ],
    },
]

if __name__ == "__main__":
    collection_or_source_url = get_source_url()
    for concept in concepts:
        send_to_ocl(collection_or_source_url, concept)
