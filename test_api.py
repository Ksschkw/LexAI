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
        "query": "What are some laws i should know but i do not?",
        "session_id": "test_session"
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        print(f"Response length: {len(response_data['response'])} characters")
        with open("test_response.txt", "w", encoding="utf-8") as f:
            f.write(response_data['response'])
        print("Full response saved to test_response.txt")
        print(f"Query Response: {response.status_code} - {response.json()}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("Running API tests...")
    test_health()
    test_query()
    print("Tests complete!")