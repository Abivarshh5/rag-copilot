import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'app'))
sys.path.append(os.getcwd())

from app.rag.engine import ingest_docs, hybrid_retrieve_docs
from app.rag.llm import generate_answer

def run_verification():
    print("1. Starting Ingestion...")
    stats = ingest_docs()
    print(f"Ingestion Stats: {stats}")
    
    print("\n2. Testing Retrieval (with Metadata check)...")
    # Query meaningful to the docs
    query = "What is the Cloud ProAdvisor Program?" 
    hits = hybrid_retrieve_docs(query, k=3)
    
    print(f"Retrieved {len(hits)} hits.")
    for i, hit in enumerate(hits):
        print(f"\nHit {i+1}:")
        print(f"  Text: {hit['text'][:100]}...")
        print(f"  Metadata: {hit.get('metadata')}")
        print(f"  Score: {hit.get('score')}")
        print(f"  Distance: {hit.get('distance')}")
        
        # Verification
        if not hit.get('metadata'):
            print("  [FAIL] Metadata missing!")
        else:
            print("  [PASS] Metadata present.")

    print("\n3. Testing Generation (with Score check)...")
    result = generate_answer(query)
    print("\nGeneration Result:")
    print(f"  Answer: {result['answer'][:100]}...")
    print(f"  Status: {result['status']}")
    print(f"  Sources: {len(result['sources'])}")
    
    for i, source in enumerate(result['sources']):
        print(f"\n  Source {i+1}:")
        print(f"    Score: {source.get('score')}")
        if 'score' in source:
             print("    [PASS] Score present.")
        else:
             print("    [FAIL] Score missing!")

if __name__ == "__main__":
    run_verification()
