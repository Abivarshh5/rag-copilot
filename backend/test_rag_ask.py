import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_ask():
    print("Testing /rag/ask...")
    
    # 1. Answerable Question
    question = "What are the key features of FastAPI?"
    print(f"\nQ: {question}")
    start = time.time()
    r = requests.post(f"{BASE_URL}/rag/ask", json={"query": question}, timeout=60)
    print(f"Time: {time.time()-start:.2f}s")
    
    if r.status_code == 200:
        data = r.json()
        print(f"Response: {json.dumps(data, indent=2)}")
    else:
        print(f"Error: {r.text}")

    # 2. Unanswerable Question (Low Context)
    question = "Who is the president of Mars?"
    print(f"\nQ: {question}")
    r = requests.post(f"{BASE_URL}/rag/ask", json={"query": question}, timeout=60)
    
    if r.status_code == 200:
        data = r.json()
        print(f"Status: {data.get('status')}")
        print(f"Answer: {data.get('answer')}")
    else:
        print(f"Error: {r.text}")

if __name__ == "__main__":
    print("Waiting for server...")
    time.sleep(5)
    test_ask()
