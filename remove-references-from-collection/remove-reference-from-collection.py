import requests
from common import get_headers, get_api_domain, get_collection_url
from remove_reference_resources import all_references
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import time


def delete_reference(reference_url):
    url = urljoin(get_api_domain(), reference_url)
    try:
        response = requests.delete(url, headers=get_headers())
        print(url, response.text)
        response.raise_for_status()
    except Exception as e:
        print(f"{reference_url}: failed to delete due to {e}")
        return


if __name__ == "__main__":
    # Rate limiter: 300 requests per 10 seconds
    BATCH_SIZE = 300
    DELAY_BETWEEN_BATCHES = 10  # seconds

    # Split references into batches
    total_references = len(all_references)
    num_batches = (total_references + BATCH_SIZE - 1) // BATCH_SIZE

    print(
        f"Processing {total_references} references in {num_batches} batches of {BATCH_SIZE}"
    )

    for batch_num in range(num_batches):
        start_idx = batch_num * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, total_references)
        batch = all_references[start_idx:end_idx]

        print(
            f"Processing batch {batch_num + 1}/{num_batches} (references {start_idx + 1}-{end_idx})"
        )

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [
                executor.submit(delete_reference, reference_url)
                for reference_url in batch
            ]
            for future in as_completed(futures):
                future.result()

        # Wait 10 seconds before processing next batch (except for the last batch)
        if batch_num < num_batches - 1:
            print(f"Waiting {DELAY_BETWEEN_BATCHES} seconds before next batch...")
            time.sleep(DELAY_BETWEEN_BATCHES)

    print("All batches processed successfully!")

    # for reference_url in all_references:
    #     delete_reference(reference_url)
