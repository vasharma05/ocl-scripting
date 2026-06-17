# get-all-concept-set-answers

Walk concept-set membership and Q-and-A mappings to collect every concept transitively reachable from one or more parent concepts.

## What it does

- Reads one or more parent concept URLs from `resources.concept_url` (string or list).
- For each parent, paginates its `mappings/` endpoint and keeps mappings whose `map_type` is `CONCEPT-SET` or `Q-AND-A`.
- Recursively follows the member/answer concepts and collects the full transitive set.
- Writes the result to `results.json`.

Useful for exporting all members of a concept set or all answers of an answer set, including nested groupings.

## Usage

1. Edit `resources.py` and set `concept_url`.
2. Run:
   ```
   python get-all-concept-set-answers/get_all_concept_set_answers.py
   ```
