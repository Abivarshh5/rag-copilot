import requests
try:
    r = requests.get("http://localhost:8000/debug_db")
    print(r.json())
except Exception as e:
    print(e)
