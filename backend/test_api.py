import requests
import json

BASE_URL = "http://localhost:8000"
results = []

def log(test_name, status, response_code, response_body):
    result = f"{test_name}: {status} (HTTP {response_code})"
    print(result)
    results.append({"test": test_name, "status": status, "code": response_code, "body": response_body})

# Test 1: Health
r = requests.get(f"{BASE_URL}/health")
log("GET /health", "PASS" if r.status_code == 200 else "FAIL", r.status_code, r.text)

# Test 2: Signup
r = requests.post(f"{BASE_URL}/auth/signup", json={"email": "finaltest@example.com", "password": "password123"})
log("POST /auth/signup", "PASS" if r.status_code in [200, 400] else "FAIL", r.status_code, r.text)

# Test 3: Login
r = requests.post(f"{BASE_URL}/auth/login", json={"email": "finaltest@example.com", "password": "password123"})
token = ""
if r.status_code == 200:
    token = r.json().get("access_token", "")
log("POST /auth/login", "PASS" if r.status_code == 200 and token else "FAIL", r.status_code, r.text[:100])

# Test 4: /auth/me without token
r = requests.get(f"{BASE_URL}/auth/me")
log("GET /auth/me (no token)", "PASS" if r.status_code in [401, 403] else "FAIL", r.status_code, r.text)

# Test 5: /auth/me with valid token
r = requests.get(f"{BASE_URL}/auth/me", headers={"Authorization": f"Bearer {token}"})
log("GET /auth/me (valid token)", "PASS" if r.status_code == 200 else "FAIL", r.status_code, r.text)

# Test 6: /auth/me with invalid token
r = requests.get(f"{BASE_URL}/auth/me", headers={"Authorization": "Bearer invalidtoken"})
log("GET /auth/me (invalid token)", "PASS" if r.status_code == 401 else "FAIL", r.status_code, r.text)

# Test 7: CORS
r = requests.options(f"{BASE_URL}/health", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"})
cors_headers = {k: v for k, v in r.headers.items() if "access-control" in k.lower()}
log("OPTIONS /health (CORS)", "PASS" if cors_headers else "FAIL", r.status_code, str(cors_headers))

# Summary
print("\n" + "=" * 40)
passed = sum(1 for r in results if r["status"] == "PASS")
print(f"SUMMARY: {passed}/{len(results)} tests passed")

# Write detailed results
with open("test_output.json", "w") as f:
    json.dump(results, f, indent=2)
print("Detailed results saved to test_output.json")
