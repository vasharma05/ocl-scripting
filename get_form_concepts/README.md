# get_form_concepts

Extract concept UUIDs and labels referenced inside OpenMRS form JSON files (O3 form schema).

## What it does

- Walks a form's `pages` → `sections` → `questions` → `answers` tree.
- Collects every `questionOptions.concept` and `answers[].concept` UUID.
- Optionally extracts labels (page, section, question, answer) for translation workflows.

This script is purely local — it does not call the OCL API.

## Usage

1. Edit `resources.py`:
   - `form_path` — directory containing form JSON files.
   - `forms` — list of form filenames to process.
2. Run:
   ```
   python get_form_concepts/get_form_concepts.py
   ```

Output is written to `results.json`.
