import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_ask():
    print("Testing /rag/ask...")
    
    # Question about FastAPI (Expect success)
    question = "What are the key features of FastAPI?"
    print(f"\nQ: {question}")
    
    try:
        r = requests.post(f"{BASE_URL}/rag/ask", json={"query": question}, timeout=60)
        
        if r.status_code == 200:
            data = r.json()
            print("Response:")
            print(json.dumps(data, indent=2))
            
            # Validation
            if data['status'] == 'ok' and len(data['answer']) > 10:
                print("\n✅ Answer generation SUCCESS")
            else:
                print("\n❌ Answer generation FAILED (Check response above)")
        else:
            print(f"Server Error: {r.status_code} - {r.text}")

    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    print("Waiting for server...")
    time.sleep(5)
    test_ask()
