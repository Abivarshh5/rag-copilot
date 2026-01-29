import requests

def test_api():
    base_url = "http://localhost:8000"
    
    # 1. Login
    print("Testing Login...")
    login_data = {"email": "test@example.com", "password": "password123"}
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"Login successful! Token: {token[:20]}...")
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return

    # 2. Ask question
    print("\nTesting RAG Ask...")
    headers = {"Authorization": f"Bearer {token}"}
    ask_data = {"query": "What is this project about?"}
    response = requests.post(f"{base_url}/rag/ask", json=ask_data, headers=headers)
    if response.status_code == 200:
        print("Ask successful!")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Ask failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    import json
    test_api()
