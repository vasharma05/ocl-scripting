# verify-concepts-in-openmrs

Verify that a list of concept UUIDs exists in a target OpenMRS instance.

## What it does

- For each UUID in `resources.py`, calls `GET {OPENMRS_DOMAIN}/{REST_API_ENDPOINT}/{uuid}` with HTTP Basic auth.
- Records present/missing UUIDs to `concepts_verification_results.json`.

## Usage

1. Edit `resources.py`:
   - `ENDPOINT_DOMAIN`, `REST_API_ENDPOINT`, `OPENMRS_USERNAME`, `OPENMRS_PASSWORD`, and the UUID list.
2. Run:
   ```
   python verify-concepts-in-openmrs/verify-concepts-in-openmrs.py
   ```
