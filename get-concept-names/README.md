# get-concept-names

Fetch the preferred name for a list of concepts in a given locale.

## What it does

- For each URL in `resources.concept_urls`, calls `GET {domain}/{concept_url}/names/`.
- Returns the `locale_preferred` name matching `resources.locale`. Falls back to any name in that locale if none is marked preferred.
- Writes three JSON files in this directory: preferred results, non-preferred results, and errors.

## Usage

1. Edit `resources.py`:
   - `concept_urls` — list of concept URLs.
   - `locale` — e.g. `"en"`, `"fr"`.
2. Run:
   ```
   python get-concept-names/get_concept_names.py
   ```
