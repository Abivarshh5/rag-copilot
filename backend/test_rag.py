import requests
import json
import time

BASE_URL = "http://localhost:8000"

def run_test(name, func):
    print(f"Running {name}...")
    try:
        func()
        print(f"✅ {name} PASSED")
    except Exception as e:
        print(f"❌ {name} FAILED: {e}")

def test_health():
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"

def test_ingest():
    # Ingest docs
    # This might take time if model is downloading
    start = time.time()
    print("Sending ingest request (this triggers model download on server)...")
    r = requests.post(f"{BASE_URL}/rag/ingest", timeout=300) 
    print(f"Ingest response ({time.time()-start:.2f}s): {r.text}")
    assert r.status_code == 200, f"Ingest failed: {r.text}"
    stats = r.json().get("stats", {})
    assert stats.get("doc_count", 0) > 0, "No docs ingested"

def test_retrieve():
    # Query: "FastAPI" (should match doc1)
    query = "FastAPI high performance"
    r = requests.post(f"{BASE_URL}/rag/retrieve", json={"query": query, "k": 2})
    assert r.status_code == 200, f"Retrieve failed: {r.text}"
    results = r.json().get("results", [])
    print(f"Query: '{query}'")
    if results:
        print(f"Top Result: {results[0]['text'][:100]}...")
        assert "FastAPI" in results[0]['text'], "Expected FastAPI in results"
    else:
        raise Exception("No results returned")

    # Query: "Newton" (should match doc2)
    query = "laws of motion"
    r = requests.post(f"{BASE_URL}/rag/retrieve", json={"query": query, "k": 2})
    results = r.json().get("results", [])
    print(f"Query: '{query}'")
    if results:
        print(f"Top Result: {results[0]['text'][:100]}...")
        assert "Newton" in results[0]['text'], "Expected Newton in results"
    else:
         raise Exception("No results returned")

if __name__ == "__main__":
    print("Waiting for server to be ready...")
    time.sleep(5)
    run_test("Health Check", test_health)
    run_test("Ingestion", test_ingest)
    run_test("Retrieval", test_retrieve)
