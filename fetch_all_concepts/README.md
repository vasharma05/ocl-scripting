# fetch_all_concepts

Download every concept from one or more OCL sources/collections and save them as a JSON file.

## What it does

- Reads `OCL_API_DOMAIN` and `OCL_API_TOKEN` from `.env`.
- Iterates over `COLLECTION_OR_SOURCE_URLS` defined at the top of `fetch_all_concepts.py`.
- Paginates through `/concepts/` for each URL using a thread pool.
- Writes the combined list to `all_<COLLECTION_OR_SOURCE_NAME>_concepts.json` inside this directory.

## Usage

1. Edit `fetch_all_concepts.py`:
   - Set `COLLECTION_OR_SOURCE_URLS` to the source/collection URLs you want to fetch.
   - Set `COLLECTION_OR_SOURCE_NAME` (used in the output filename).
2. Run:
   ```
   python fetch_all_concepts/fetch_all_concepts.py
   ```
