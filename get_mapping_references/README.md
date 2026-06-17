# get_mapping_references

Fetch all mappings (in either direction) for a list of concept URLs.

## What it does

- For each concept in `resources.concept_urls`, paginates `GET {domain}/{concept_url}/mappings/`.
- Keeps mappings where the concept appears as either `from_concept_url` or `to_concept_url`.
- Writes the per-concept mapping list to `results.json`.

## Usage

1. Edit `resources.py` to set `concept_urls`.
2. Run:
   ```
   python get_mapping_references/get_mapping_references.py
   ```
