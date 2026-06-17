# add-concept-names

Add additional names (e.g. translations) to existing OCL concepts.

## What it does

- Reads `(concept_url, concept_name)` pairs from `add_concept_name_resources.py`.
- POSTs each name to `{concept_url}/names/` using a thread pool with batching to avoid OCL rate limits.

## Usage

1. Edit `add_concept_name_resources.py`:
   - Provide the list of concept URLs and the name dicts (`name`, `locale`, `name_type`, `locale_preferred`, etc.) to add.
2. Run:
   ```
   python add-concept-names/add-concept-names.py
   ```
