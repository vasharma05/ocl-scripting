# are_concepts_present

Check whether a list of concepts is present in a given OCL source or collection.

## What it does

- Prompts for the source/collection URL and whether the input list contains concept URLs or concept IDs/names.
- For each concept, queries `/references/?q=...` (for concept URLs) or `/concepts/?q=...` (for IDs/names) on the target source or collection.
- Splits results into `present` and `absent` and writes them to `concept_present_map.json`.

## Usage

1. Edit `are_concepts_present_resources.py`:
   - `all_concepts` — list of concept URLs or IDs to look up.
2. Run:
   ```
   python are_concepts_present/are-concepts-present.py
   ```
3. Answer the prompts (`org`, source vs collection, name, "Is this a concept url?").

Requests are sent with the OCL `Authorization` header so private sources/collections work.
