import requests
import json
import time

BASE_URL = "http://localhost:8000"

def run_test():
    print("Waiting for server...")
    time.sleep(10) # Wait for model load
    
    # 1. SUCCESS CASE
    print("\n1. Testing Success Case: 'What is FastAPI?'")
    try:
        r = requests.post(f"{BASE_URL}/rag/ask", json={"query": "What is FastAPI?"})
        print(f"Status Code: {r.status_code}")
        print(f"Response: {json.dumps(r.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

    # 2. LOW CONTEXT CASE
    print("\n2. Testing Low Context Case: 'Who is the president of Mars?'")
    try:
        r = requests.post(f"{BASE_URL}/rag/ask", json={"query": "Who is the president of Mars?"})
        print(f"Status Code: {r.status_code}")
        print(f"Response: {json.dumps(r.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_test()
