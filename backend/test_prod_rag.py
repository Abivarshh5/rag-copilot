import requests

BASE_URL = "https://abiramavarshini-rag-backend.hf.space"

def test_ask(query):
    print(f"Asking: {query}")
    try:
        r = requests.post(f"{BASE_URL}/rag/ask", json={"query": query})
        if r.status_code == 200:
            res = r.json()
            print(f"Answer: {res.get('answer')}")
            print(f"Sources: {[s.get('title') for s in res.get('sources', [])]}")
            print(f"Status: {res.get('status')}")
        else:
            print(f"Error: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    # Test a question that should be in Zoom_FAQ-v9.pdf
    test_ask("How do I join a Zoom meeting?")
