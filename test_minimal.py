"""Minimal endpoint test"""
import requests as r, json

BASE = "http://localhost:8001"

# Just test login
login = r.post(f"{BASE}/auth/login", json={"email": "gonzifracchia@gmail.com", "password": "gonzalo123"}, timeout=30)
print(f"Login: {login.status_code}")
if login.status_code == 200:
    print("User login OK")
    cookie = login.cookies.get("access_token", "")
    resp = r.get(f"{BASE}/api/v1/pagos/33", cookies={"access_token": cookie}, timeout=30)
    print(f"Pago 33: {resp.status_code}")
    print(json.dumps(resp.json(), indent=2))
else:
    print(f"Failed: {login.text[:200]}")

# Test admin
login2 = r.post(f"{BASE}/auth/login", json={"email": "admin@admin.com", "password": "admin123"}, timeout=30)
print(f"\nAdmin login: {login2.status_code}")
if login2.status_code == 200:
    cookie2 = login2.cookies.get("access_token", "")
    resp2 = r.get(f"{BASE}/api/v1/pagos/33", cookies={"access_token": cookie2}, timeout=30)
    print(f"Pago 33 (admin): {resp2.status_code}")
    print(resp2.text[:300])
