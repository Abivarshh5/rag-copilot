import requests
import json

BASE_URL = "https://abiramavarshini-rag-backend.hf.space"

def test_endpoint(name, method, path, params=None, json_data=None):
    url = f"{BASE_URL}{path}"
    print(f"\n--- Testing {name} [{method} {path}] ---")
    try:
        if method == "GET":
            response = requests.get(url, params=params)
        else:
            response = requests.post(url, json=json_data)
        
        print(f"Status: {response.status_code}")
        print("Response Content:")
        print(json.dumps(response.json(), indent=2))
        return response.json()
    except Exception as e:
        print(f"FAILED: {e}")
        return None

if __name__ == "__main__":
    # 1. Health
    h = test_endpoint("Health", "GET", "/health")
    if h and h.get("status") == "ok": print("✅ Health OK")
    
    # 2. Auth Debug
    a = test_endpoint("Auth Debug", "GET", "/auth/debug_login", params={
        "email": "test@example.com", "password": "password"
    })
    if a and a.get("status") == "success": print("✅ Auth OK")
    
    # 3. RAG Ask (In-context)
    r = test_endpoint("RAG Ask (Slack)", "POST", "/rag/ask", json_data={
        "query": "What are the common Slack FAQs in the guide?"
    })
    if r and r.get("status") == "success": 
        print("✅ RAG Document Match OK")
        print(f"   Source: {r['sources'][0]['title'] if r['sources'] else 'None'}")
    
    # 4. RAG Ask (Out-of-context)
    o = test_endpoint("RAG Ask (France)", "POST", "/rag/ask", json_data={
        "query": "What is the capital of France?"
    })
    if o and "This info is not in your documents" in o.get("answer", ""):
        print("✅ RAG General Fallback OK")
        print(f"   Response Prefix: {o['answer'][:50]}...")
