# remove-references-from-collection

Bulk-delete references from an OCL collection.

## What it does

- Reads reference URLs from `remove_reference_resources.all_references`.
- For each URL, sends `DELETE {domain}/{reference_url}`. Requests are batched with a sleep between batches to avoid OCL rate limits.

## Usage

1. Edit `remove_reference_resources.py` to set `all_references` to the list of reference URLs to remove.
2. Run:
   ```
   python remove-references-from-collection/remove-reference-from-collection.py
   ```

> Deletions are irreversible. Double-check the reference list before running.
