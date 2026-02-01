import requests
import json
import sys

BASE_URL = "http://localhost:8000/rag/ask"

test_cases = [
    {
        "category": "Communication (Slack)",
        "query": "How do I manage notifications in Slack?"
    },
    {
        "category": "Storage (Dropbox)",
        "query": "How does Dropbox billing work?"
    },
    {
        "category": "Recruiting",
        "query": "What is the process for recruiting coordination?"
    }
]

print(f"Testing RAG Endpoint: {BASE_URL}\n")

for test in test_cases:
    print(f"--- Testing: {test['category']} ---")
    print(f"Query: {test['query']}")
    
    try:
        response = requests.post(BASE_URL, json={"query": test['query']})
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"Answer: {data.get('answer')[:150]}...") # Print first 150 chars
            
            sources = data.get('sources', [])
            print(f"Source Count: {len(sources)}")
            
            if sources:
                first_source = sources[0]
                metadata = first_source.get('metadata', {})
                title = metadata.get('title', 'N/A')
                score = first_source.get('score', 0)
                print(f"Top Source: {title} (Score: {score:.4f})")
            else:
                print("WARNING: No sources returned!")
                
        else:
            print(f"Error: HTTP {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Exception: {e}")
    
    print("\n")
