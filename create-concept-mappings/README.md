# create-concept-mappings

Bulk-create mappings between concepts in an OCL source.

## What it does

- Reads mappings from `resources.mappings`. Each entry specifies `from_concept_url`, `to_concept_url`, and `map_type`.
- Prompts for the target source URL.
- POSTs each mapping to `{source_url}/mappings/` using a thread pool.

## Usage

1. Edit `resources.py` to set the `mappings` list.
2. Run:
   ```
   python create-concept-mappings/create-concept-mappings.py
   ```
