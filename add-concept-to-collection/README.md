# add-concept-to-collection

Add concept references to an OCL collection in batches.

## What it does

- Reads concept URLs from `add_concept_resources.concept_urls_to_add`.
- Prompts for the target collection URL.
- Splits the list into batches and PUTs each batch as `{"data": [{"expression": <url>}, ...]}` to `{collection_url}/references/`, sleeping between batches.

## Usage

1. Edit `add_concept_resources.py` to set `concept_urls_to_add`.
2. Run:
   ```
   python add-concept-to-collection/add-concept-to-collection.py
   ```
