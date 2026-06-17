# verify-reference-collection

Verify that a list of concept references is present in a target OCL collection.

## What it does

- Prompts for the collection URL.
- For each concept URL in `resources.concepts`, calls `GET {collection_url}/references?q={concept_url}`.
- Classifies each lookup as `found`, `not_found`, or `error` and writes the summary to `results.json`.

## Usage

1. Edit `resources.py` and set `concepts`.
2. Run:
   ```
   python verify-reference-collection/verify-reference-in-collection.py
   ```
