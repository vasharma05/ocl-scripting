from utils import get_api_domain, get_headers
from urllib.parse import urljoin
import requests

concepts_to_clone = [
    "/orgs/CIEL/sources/CIEL/concepts/160218/",
    "/orgs/CIEL/sources/CIEL/concepts/5622/",
    "/orgs/CIEL/sources/CIEL/concepts/166078/",
    "/orgs/CIEL/sources/CIEL/concepts/124193/",
    "/orgs/CIEL/sources/CIEL/concepts/116030/",
    "/orgs/CIEL/sources/CIEL/concepts/151673/",
    "/orgs/CIEL/sources/CIEL/concepts/1067/",
]


url = urljoin(get_api_domain(), "/orgs/UVL-Burundi/sources/uvl-ciel/concepts/$clone/")

body = {
    "expressions": concepts_to_clone,
    "parameters": {
        "mapTypes": "Q-AND-A,CONCEPT-SET",
        "excludeMapTypes": "",
        "returnMapTypes": "*",
        "cascadeLevels": "*",
        "equivalencyMapType": "SAME-AS",
    },
}
response = requests.post(url, json=body, headers=get_headers())
response.raise_for_status()
print(response.json())
