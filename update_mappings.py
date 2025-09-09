from utils import get_headers, get_api_domain
from compare import old_to_new_map
import json
from urllib.parse import urljoin


with open("./all_mappings.json", "r") as f:
    data = json.load(f)

all_mappings = data["all_mappings"]

new_mappings = []

for mapping in all_mappings:
    new_mapping = {
        "map_type": mapping["map_type"],
        "from_concept_url": mapping["from_concept_url"],
    }
    if mapping["to_concept_url"] in old_to_new_map:
        new_mapping["to_concept_url"] = old_to_new_map[mapping["to_concept_url"]]
    else:
        print(mapping["to_concept_url"], "not found")
    new_mappings.append(new_mapping)

with open("./mappings_updated.json", "w") as f:
    json.dump(new_mappings, f, indent=4)
