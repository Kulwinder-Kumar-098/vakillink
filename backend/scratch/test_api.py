import requests
import json

def test_api():
    url = "http://localhost:8000/api/v1/ai/retrieve"
    payload = {
        "query": "criminal",
        "top_k": 5
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Number of results: {len(data)}")
            if data:
                print("First result:")
                print(json.dumps(data[0], indent=2))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    test_api()
