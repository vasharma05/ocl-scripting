# OCL Concept Set Scripts

A collection of Python scripts for managing concepts, mappings, references, and collections on [Open Concept Lab (OCL)](https://openconceptlab.org/). These scripts automate common bulk operations against the OCL API that are tedious or unsupported through the UI.

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Create a `.env` file at the repository root with:
   ```
   OCL_API_DOMAIN=https://api.openconceptlab.org
   OCL_API_TOKEN=<your OCL API token>
   ```
3. Most scripts read input from a sibling `resources.py` (or `*_resources.py`) file in the same directory — edit those to point at the source/collection and concepts you want to operate on.

Shared helpers live in `utils.py` (root) and a per-script `common.py` that exposes `get_api_domain()`, `get_headers()`, and prompts for source/collection URLs.

## Scripts

### Read / verify

- [fetch_all_concepts](fetch_all_concepts/README.md) — Download every concept from one or more OCL sources/collections to JSON.
- [fetch_all_references.py](#fetch_all_referencespy) — Download every reference expression from one or more OCL collections.
- [get-concept-names](get-concept-names/README.md) — Fetch the preferred name (per locale) for a list of concept URLs.
- [get_form_concepts](get_form_concepts/README.md) — Parse OpenMRS form JSON files and extract referenced concept UUIDs and labels.
- [get_mapping_references](get_mapping_references/README.md) — Pull all mappings for a list of concepts.
- [get-all-concept-set-answers](get-all-concept-set-answers/README.md) — Walk `CONCEPT-SET` and `Q-AND-A` mappings to collect set members and answer concepts.
- [are_concepts_present](are_concepts_present/README.md) — Check whether a list of concepts exists in a given source/collection.
- [verify-reference-collection](verify-reference-collection/README.md) — Verify that specific concept references are present in a collection.
- [verify-concepts-in-openmrs](verify-concepts-in-openmrs/README.md) — Verify concept UUIDs exist in an OpenMRS instance.

### Create / update

- [create-concept-mappings](create-concept-mappings/README.md) — Bulk-create mappings between concepts.
- [add-concept-names](add-concept-names/README.md) — Add additional names to existing concepts.
- [add-concept-to-collection](add-concept-to-collection/README.md) — Add concept references to a collection in batches.
- [set-concept-names-preferred](set-concept-names-preferred/README.md) — Toggle the `locale_preferred` flag on existing concept names.

### Delete

- [remove-references-from-collection](remove-references-from-collection/README.md) — Bulk-delete references from a collection.

## fetch_all_references.py

Top-level script that paginates through `/.../references/` for one or more configured OCL collections and writes every reference expression to a JSON file. Configure target collection URLs at the top of the script.

```
python fetch_all_references.py
```

## Conventions

- All OCL requests go through `get_headers()`, which attaches `Authorization: Token <OCL_API_TOKEN>` — if you add a new request, use this helper rather than calling `requests` bare.
- Long-running scripts use `ThreadPoolExecutor` for concurrency and process inputs in batches with a sleep between batches to avoid OCL rate limits.
- Results are typically written to a sibling `results.json` (or similar) in the same directory.
