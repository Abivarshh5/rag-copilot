import requests

url = "http://localhost:8000/auth/login"
payload = {
    "email": "test_manual@example.com",
    "password": "password123"
}
headers = {"Content-Type": "application/json"}

try:
    print(f"Testing local Login at: {url}")
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
