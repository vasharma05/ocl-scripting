# set-concept-names-preferred

Toggle the `locale_preferred` flag on existing concept names.

## What it does

For each entry in `resources.concept_names`:
1. Fetches the concept's names via `GET {concept_url}/names/`.
2. Finds the name matching `resources.locale_name` and `resources.name_type`.
3. Sets `locale_preferred` to `resources.locale_preferred` and PATCHes the concept with the updated names list.

Results (updated / skipped / errors) are written to `results.json`.

## Usage

1. Edit `resources.py`:
   - `concept_names` — list of `(concept_url, expected_name)` entries.
   - `locale_name`, `name_type`, `locale_preferred` — selection and target value.
2. Run:
   ```
   python set-concept-names-preferred/set_concept_names_preferred.py
   ```
