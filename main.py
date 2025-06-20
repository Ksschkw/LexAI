# Purpose: Serves as the entry point for LEXAI, with server and interactive modes.
# Why: Explicitly supports both deployment and local testing.

import sys
from view.api.endpoints import app
from fastapi.testclient import TestClient
import uvicorn

def run_interactive_loop():
    """Runs an interactive loop for local testing of LEXAI.
    
    Why: Mirrors MYRAGAGENT's local testing feature for quick debugging.
    """
    print("Welcome to LEXAI! Type 'exit' to quit.")
    session_id = "local_test_session"
    client = TestClient(app)
    while True:
        query = input("Enter your legal query: ")
        if query.lower() == "exit":
            print("Goodbye!")
            break
        try:
            response = client.post(
                "/query",
                json={"query": query, "session_id": session_id}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"Query: {query}\nLEXAI Response: {data['response']}\n")
            else:
                print(f"Error: {response.status_code} - {response.text}\n")
        except Exception as e:
            print(f"Error processing query: {e}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--server":
        # Run as server for deployment
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        # Run interactive loop for local testing
        run_interactive_loop()