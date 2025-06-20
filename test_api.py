import requests
import json

# Base URL of your running server
BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """Test the /health endpoint."""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Status: {response.status_code} - {response.text}")

def test_query():
    """Test the /query endpoint."""
    url = f"{BASE_URL}/query"
    payload = {
        "query": "What are my fundamental human rights?",
        "session_id": "test_session"
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    if response.status_code == 200:
        print(f"Query Response: {response.status_code} - {response.json()}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("Running API tests...")
    test_health()
    test_query()
    print("Tests complete!")