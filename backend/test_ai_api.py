import requests
import json

url = "http://127.0.0.1:9000/api/v1/query"
payload = {
    "query": "Case Type: Property Dispute. Complexity: Standard. Opposing Party: Individual. Incident Date: 2023-01-01. Description: Ancestral property inheritance dispute in Mumbai. Share of home denied by brother."
}
headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=4))
except Exception as e:
    print(f"Error: {e}")
